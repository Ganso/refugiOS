#!/bin/bash
# Generador automatizado de la imagen base de refugiOS para dispositivos externos
set -e

# Configuración de variables
IMG_SIZE="${1:-16G}"

# Validar el formato del tamaño (ej. 16G, 8G, 500M)
if [[ ! "$IMG_SIZE" =~ ^[0-9]+[GMK]$ ]]; then
    echo "ERROR: El tamaño de la imagen debe ser un número seguido de G, M o K (ej. 16G, 8G, 500M)."
    exit 1
fi

IMG_NAME="refugios-base-${IMG_SIZE}.img"
MNT_DIR="/mnt/refugios_build"
DEBIAN_RELEASE="bookworm"
USER_NAME="refugios"
USER_PASS="refugios"

# Verificar compatibilidad del sistema operativo host (requiere base Debian)
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ ! "$ID" =~ (debian|ubuntu|mint|pop) ]] && [[ ! "$ID_LIKE" =~ (debian|ubuntu) ]]; then
        echo "=========================================================="
        echo " ERROR: Sistema operativo host no soportado."
        echo "=========================================================="
        echo " El script de construcción de la imagen de refugiOS requiere"
        echo " un sistema operativo basado en Debian (Debian, Ubuntu, Mint, Pop!_OS)."
        echo " Sistema detectado: $NAME ($ID)"
        echo "=========================================================="
        exit 1
    fi
else
    echo "ERROR: No se pudo determinar el sistema operativo. Se requiere un sistema basado en Debian."
    exit 1
fi

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Este script debe ser ejecutado como root (sudo)."
    exit 1
fi

LOOP_DEV=""

# Función de limpieza robusta (trap)
cleanup() {
    local exit_code=$?
    echo "=> Realizando limpieza de montajes y dispositivos..."
    
    # Desmontar en orden inverso
    for mp in "$MNT_DIR/dev/pts" "$MNT_DIR/dev" "$MNT_DIR/sys" "$MNT_DIR/proc" "$MNT_DIR/run" "$MNT_DIR/boot/efi" "$MNT_DIR"; do
        if mountpoint -q "$mp" 2>/dev/null; then
            echo "Desmontando $mp..."
            umount "$mp" || umount -lf "$mp" || true
        fi
    done
    
    # Desasociar dispositivo loop
    if [ -n "$LOOP_DEV" ]; then
        if losetup -a | grep -q "$LOOP_DEV"; then
            echo "Desasociando loop device $LOOP_DEV..."
            losetup -d "$LOOP_DEV" || true
        fi
    fi
    
    if [ $exit_code -ne 0 ]; then
        echo "=> ERROR: La construcción de la imagen falló."
    fi
}
trap cleanup EXIT

echo "=> Iniciando la construcción de refugiOS..."

# 1. Instalar dependencias en el host (si faltan)
apt-get update
apt-get install -y debootstrap parted dosfstools e2fsprogs

# 2. Crear el archivo de imagen esparso (rápido)
echo "=> Creando imagen de ${IMG_SIZE}..."
truncate -s $IMG_SIZE $IMG_NAME

# 3. Particionar la imagen (GPT: EFI + Root)
echo "=> Particionando..."
parted -s $IMG_NAME mklabel gpt
parted -s $IMG_NAME mkpart EFI fat32 1MiB 513MiB
parted -s $IMG_NAME set 1 esp on
parted -s $IMG_NAME mkpart ROOT ext4 513MiB 100%

# 4. Mapear la imagen a dispositivos loop
LOOP_DEV=$(losetup -Pf --show $IMG_NAME)
LOOP_EFI="${LOOP_DEV}p1"
LOOP_ROOT="${LOOP_DEV}p2"

echo "=> Formateando particiones..."
mkfs.vfat -F32 $LOOP_EFI
mkfs.ext4 -F $LOOP_ROOT

# Obtener UUIDs para fstab
UUID_EFI=$(blkid -s UUID -o value $LOOP_EFI)
UUID_ROOT=$(blkid -s UUID -o value $LOOP_ROOT)

# 5. Montar sistemas de archivos
mkdir -p $MNT_DIR
mount $LOOP_ROOT $MNT_DIR
mkdir -p $MNT_DIR/boot/efi
mount $LOOP_EFI $MNT_DIR/boot/efi

# 6. Instalar el sistema base con debootstrap
echo "=> Ejecutando debootstrap (esto llevará unos minutos)..."
debootstrap --arch=amd64 $DEBIAN_RELEASE $MNT_DIR http://deb.debian.org/debian/

# Generar /etc/fstab para evitar advertencias de UUIDs y asegurar montajes correctos en arranque
cat << FSTAB > $MNT_DIR/etc/fstab
# /etc/fstab: información estática de los sistemas de archivos de refugiOS
UUID=$UUID_ROOT  /          ext4  errors=remount-ro  0  1
UUID=$UUID_EFI   /boot/efi  vfat  umask=0077          0  2
FSTAB

# 7. Preparar el entorno chroot
mount --bind /dev $MNT_DIR/dev
mount --bind /dev/pts $MNT_DIR/dev/pts
mount --bind /proc $MNT_DIR/proc
mount --bind /sys $MNT_DIR/sys
mount --bind /run $MNT_DIR/run

echo "=> Configurando el sistema dentro del chroot..."

# 8. Ejecutar comandos DENTRO del chroot
chroot $MNT_DIR /bin/bash <<EOF
# Configurar repositorios
cat << 'SOURCES' > /etc/apt/sources.list
deb http://deb.debian.org/debian/ bookworm main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
deb http://deb.debian.org/debian/ bookworm-updates main contrib non-free non-free-firmware
SOURCES

apt-get update
apt-get install -y linux-image-amd64 grub-efi-amd64 sudo network-manager \
                   xfce4 xfce4-terminal curl cloud-guest-utils zenity lightdm \
                   epiphany-browser

# Crear un device.map temporal para mapear el loop device como hd0
mkdir -p /boot/grub
echo "(hd0) $LOOP_DEV" > /boot/grub/device.map

# Desactivar advertencias de os-prober en update-grub
if [ -f /etc/default/grub ]; then
    if ! grep -q "GRUB_DISABLE_OS_PROBER" /etc/default/grub; then
        echo "GRUB_DISABLE_OS_PROBER=true" >> /etc/default/grub
    fi
fi

# Instalar GRUB para medios removibles (vital para pendrives) y sin registrar en NVRAM del host
grub-install --target=x86_64-efi --efi-directory=/boot/efi --removable --no-nvram
update-grub

# Eliminar el device.map para que no quede en la imagen final
rm -f /boot/grub/device.map

# Configurar usuario por defecto
useradd -m -s /bin/bash $USER_NAME
echo "$USER_NAME:$USER_PASS" | chpasswd
usermod -aG sudo $USER_NAME

# Configurar sudo sin contraseña para el usuario por defecto
mkdir -p /etc/sudoers.d
echo "$USER_NAME ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER_NAME
chmod 0440 /etc/sudoers.d/$USER_NAME

# Configurar hostname y hosts
echo "refugios" > /etc/hostname
cat << 'HOSTS' > /etc/hosts
127.0.0.1   localhost
127.0.1.1   refugios

# The following lines are desirable for IPv6 capable hosts
::1         localhost ip6-localhost ip6-loopback
ff02::1     allnodes
ff02::2     allrouters
HOSTS

# Configurar Autologin en LightDM para el usuario por defecto
mkdir -p /etc/lightdm/lightdm.conf.d
cat << 'LIGHTDM_CONF' > /etc/lightdm/lightdm.conf.d/autologin.conf
[Seat:*]
autologin-user=refugios
autologin-user-timeout=0
LIGHTDM_CONF
groupadd -r autologin || true
usermod -aG autologin $USER_NAME

# Inyectar Script de Autoexpansión Universal (NVMe/eMMC/SATA/loop)
cat << 'EXPAND_SCRIPT' > /usr/local/bin/refugios-expand.sh
#!/bin/bash
set -e
echo "=> Iniciando autoexpansión del disco de refugiOS..."
ROOT_PART=\$(findmnt -n -o SOURCE /)
PART_NAME=\$(basename "\$ROOT_PART")
PART_PATH=\$(readlink -f "/sys/class/block/\$PART_NAME")
DISK_NAME=\$(basename "\$(dirname "\$PART_PATH")")
DISK="/dev/\$DISK_NAME"
PART_NUM=\$(cat "/sys/class/block/\$PART_NAME/partition")

echo "Expandiendo partición \$PART_NUM en disco \$DISK..."
growpart "\$DISK" "\$PART_NUM" || [ \$? -eq 1 ]
echo "Redimensionando el sistema de archivos \$ROOT_PART..."
resize2fs "\$ROOT_PART"
echo "Deshabilitando servicio de autoexpansión..."
systemctl disable refugios-expand.service
echo "=> Autoexpansión completada con éxito."
EXPAND_SCRIPT
chmod +x /usr/local/bin/refugios-expand.sh

# Inyectar Servicio de Autoexpansión
cat << 'EXPAND_SVC' > /etc/systemd/system/refugios-expand.service
[Unit]
Description=Autoexpansión del disco de refugiOS
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/refugios-expand.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EXPAND_SVC
systemctl enable refugios-expand.service

# Inyectar wrapper para comprobación de conexión antes de instalar
cat << 'WRAPPER_SCRIPT' > /usr/local/bin/refugios-install-wrapper.sh
#!/bin/bash
echo "=> Comprobando conexión a Internet con github.com..."
if ping -c 1 -W 3 github.com >/dev/null 2>&1; then
    echo "=> Conexión exitosa. Iniciando instalador..."
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
else
    # Si hay sesión de X11 y zenity está instalado, mostrar cuadro de diálogo gráfico
    if [ -n "\$DISPLAY" ] && command -v zenity >/dev/null 2>&1; then
        zenity --error \\
               --title="Sin conexión a Internet - refugiOS" \\
               --text="No se pudo conectar con github.com.\n\nPor favor, conéctate a una red WiFi o cableada (puedes usar el icono de red de NetworkManager en la bandeja de sistema) antes de intentar la instalación." \\
               --width=450
    else
        echo ""
        echo "=========================================================="
        echo " ERROR: No hay conexión con github.com"
        echo "=========================================================="
        echo " Para completar la instalación, necesitas conexión a Internet."
        echo " Por favor, conéctate a una red WiFi o cableada."
        echo " Puedes usar 'nmtui' en terminal o el panel de red."
        echo "=========================================================="
        echo ""
        echo "Presiona ENTER para cerrar..."
        read
    fi
fi
WRAPPER_SCRIPT
chmod +x /usr/local/bin/refugios-install-wrapper.sh

# Inyectar el lanzador del instalador en el Escritorio por defecto que llama al wrapper
mkdir -p /etc/skel/Desktop
cat << 'LAUNCHER' > /etc/skel/Desktop/Instalar_refugiOS.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Completar instalación de refugiOS
Comment=Descarga e instala módulos desde GitHub
Exec=xfce4-terminal -e "/usr/local/bin/refugios-install-wrapper.sh"
Icon=system-software-install
Terminal=false
Categories=System;
LAUNCHER
chmod +x /etc/skel/Desktop/Instalar_refugiOS.desktop

# Asegurar que el usuario ya creado reciba el lanzador con permisos correctos
mkdir -p /home/$USER_NAME/Desktop
cp /etc/skel/Desktop/Instalar_refugiOS.desktop /home/$USER_NAME/Desktop/
chmod +x /home/$USER_NAME/Desktop/Instalar_refugiOS.desktop
chown -R $USER_NAME:$USER_NAME /home/$USER_NAME/Desktop

# Ocultar iconos por defecto del escritorio XFCE (Home, Filesystem, Trash, Removable)
mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml
cat << 'XFCE_DESKTOP_XML' > /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="desktop-icons" type="empty">
    <property name="file-icons" type="empty">
      <property name="show-home" type="bool" value="false"/>
      <property name="show-trash" type="bool" value="false"/>
      <property name="show-filesystem" type="bool" value="false"/>
      <property name="show-removable" type="bool" value="false"/>
    </property>
  </property>
</channel>
XFCE_DESKTOP_XML
chmod 644 /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml

# Inyectar script de autostart para marcar el lanzador como de confianza en el primer login
cat << 'TRUST_SCRIPT' > /usr/local/bin/refugios-trust-launcher.sh
#!/bin/bash
# Marcar el instalador como ejecutable y confiable en GIO/XFCE
LAUNCHER_PATH="\$HOME/Desktop/Instalar_refugiOS.desktop"
if [ -f "\$LAUNCHER_PATH" ]; then
    chmod +x "\$LAUNCHER_PATH"
    if command -v gio >/dev/null 2>&1; then
        CHECKSUM=\$(sha256sum "\$LAUNCHER_PATH" | awk '{print \$1}')
        gio set "\$LAUNCHER_PATH" metadata::xfce-exe-checksum "\$CHECKSUM"
    fi
fi
TRUST_SCRIPT
chmod +x /usr/local/bin/refugios-trust-launcher.sh

# Configurar el autostart para que ejecute el script de confianza al iniciar sesión
mkdir -p /etc/xdg/autostart
cat << 'TRUST_AUTOSTART' > /etc/xdg/autostart/refugios-desktop-trust.desktop
[Desktop Entry]
Type=Application
Name=Trust Desktop Launcher
Exec=/usr/local/bin/refugios-trust-launcher.sh
OnlyShowIn=XFCE;
StartupNotify=false
Terminal=false
TRUST_AUTOSTART
chmod +x /etc/xdg/autostart/refugios-desktop-trust.desktop

# Inyectar script de bienvenida para el primer arranque gráfico
cat << 'WELCOME_SCRIPT' > /usr/local/bin/refugios-welcome.sh
#!/bin/bash
# Popup de bienvenida al primer arranque de refugiOS (se autoelimina tras ejecutarse)
MARKER="\$HOME/.refugios-welcome-done"
if [ -f "\$MARKER" ]; then
    exit 0
fi

# Obtener tamaño real del disco
ROOT_PART=\$(findmnt -n -o SOURCE /)
PART_NAME=\$(basename "\$ROOT_PART")
PART_PATH=\$(readlink -f "/sys/class/block/\$PART_NAME")
DISK_NAME=\$(basename "\$(dirname "\$PART_PATH")")
DISK_SIZE_BYTES=\$(cat "/sys/class/block/\$DISK_NAME/size" 2>/dev/null)
if [ -n "\$DISK_SIZE_BYTES" ]; then
    DISK_SIZE_GB=\$(( DISK_SIZE_BYTES * 512 / 1073741824 ))
else
    DISK_SIZE_GB="?"
fi

zenity --info \
       --title="¡Bienvenido a refugiOS!" \
       --width=500 \
       --text="<b>¡Bienvenido a refugiOS!</b>\n\nTu sistema se ha configurado correctamente en un dispositivo de <b>\${DISK_SIZE_GB} GB</b>.\n\n<b>Pasos recomendados:</b>\n\n1. <b>Ajusta la resolución de pantalla</b> en:\n   <i>Applications → Settings → Display</i>\n   (Por defecto puede estar en 640×480)\n\n2. <b>Haz doble clic en el icono del escritorio</b>\n   \"Completar instalación de refugiOS\"\n   para finalizar la configuración del sistema.\n\n¡Disfruta de refugiOS!"

touch "\$MARKER"
WELCOME_SCRIPT
chmod +x /usr/local/bin/refugios-welcome.sh

# Autostart del popup de bienvenida
cat << 'WELCOME_AUTOSTART' > /etc/xdg/autostart/refugios-welcome.desktop
[Desktop Entry]
Type=Application
Name=refugiOS Welcome
Exec=/usr/local/bin/refugios-welcome.sh
OnlyShowIn=XFCE;
StartupNotify=false
Terminal=false
WELCOME_AUTOSTART
chmod +x /etc/xdg/autostart/refugios-welcome.desktop

# Limpieza de apt
apt-get clean
EOF

# 9. Desmontar y limpiar
echo "=> Limpiando y desmontando de forma normal..."
umount $MNT_DIR/sys
umount $MNT_DIR/proc
umount $MNT_DIR/run
umount $MNT_DIR/dev/pts
umount $MNT_DIR/dev
umount $MNT_DIR/boot/efi
umount $MNT_DIR
losetup -d $LOOP_DEV

echo "=> ¡Imagen $IMG_NAME generada con éxito!"