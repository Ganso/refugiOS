#!/bin/bash
# Generador automatizado de la imagen base de refugiOS para dispositivos externos
set -e

# Configuración de variables
IMG_SIZE="8G"
REFUGIOS_LANG="es"

while getopts "s:l:" opt; do
    case $opt in
        s) IMG_SIZE="$OPTARG" ;;
        l) REFUGIOS_LANG="$OPTARG" ;;
        :) echo "ERROR: La opción -$OPTARG requiere un argumento."; exit 1 ;;
        \?) echo "Uso: $0 [-s TAMAÑO] [-l IDIOMA]"; echo "  -s TAMAÑO   Tamaño de la imagen (ej. 16G, 8G). Por defecto: 8G"; echo "  -l IDIOMA   Idioma: 'es' o 'en'. Por defecto: es"; exit 1 ;;
    esac
done

# Validar el formato del tamaño
if [[ ! "$IMG_SIZE" =~ ^[0-9]+[GMK]$ ]]; then
    echo "ERROR: El tamaño de la imagen debe ser un número seguido de G, M o K (ej. 16G, 8G, 500M)."
    exit 1
fi

# Validar el idioma
if [[ "$REFUGIOS_LANG" != "es" && "$REFUGIOS_LANG" != "en" ]]; then
    echo "ERROR: Idioma no soportado '$REFUGIOS_LANG'. Use 'es' o 'en'."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/build_refugios_$(date +%Y%m%d_%H%M%S).log"
IMG_NAME="refugios-base-${IMG_SIZE}-${REFUGIOS_LANG}.img"
MNT_DIR="/mnt/refugios_build"
DEBIAN_RELEASE="bookworm"
USER_NAME="refugios"
USER_PASS="refugios"

# Redirigir toda la salida a consola Y archivo de log
exec > >(tee -i "$LOG_FILE") 2>&1

# Configuración de idioma y cadenas traducidas
if [ "$REFUGIOS_LANG" = "en" ]; then
    REFUGIOS_LOCALE="en_US.UTF-8"
    REFUGIOS_KBD="us"
    REFUGIOS_LANGUAGE="en"
    WELCOME_TITLE="Welcome to refugiOS!"
    WELCOME_BODY_START="Your system has been configured correctly on a"
    WELCOME_STEPS_LABEL="Recommended steps"
    WELCOME_STEP1="<b>Adjust screen resolution if needed</b> in:\n   <i>Applications → Settings → Display</i>"
    WELCOME_STEP2="<b>Connect to a WiFi or wired network</b>\n   (only needed during installation)\n   You can configure the network in:\n   <i>Applications → Settings → Advanced Network Configuration</i>"
    LAUNCHER_NAME="Complete refugiOS installation"
    WELCOME_STEP3="<b>Double-click the desktop icon</b>\n   «$LAUNCHER_NAME»\n   to finalize system configuration."
    WELCOME_FOOTER="Enjoy refugiOS!"
    LAUNCHER_COMMENT="Download and install modules from GitHub"
    WRAPPER_PING="Checking Internet connection with github.com..."
    WRAPPER_OK="Connection successful. Starting installer..."
    WRAPPER_ERR_TITLE="No Internet connection - refugiOS"
    WRAPPER_ERR_TEXT="Could not connect to github.com.\n\nPlease connect to a WiFi or wired network\n(you can use the network icon in the system tray)\nbefore attempting the installation."
    WRAPPER_CONSOLE_ERR="ERROR: No connection to github.com"
    WRAPPER_CONSOLE_TEXT1="To complete the installation, you need an Internet connection."
    WRAPPER_CONSOLE_TEXT2="Please connect to a WiFi or wired network."
    WRAPPER_CONSOLE_TEXT3="You can use 'nmtui' in terminal or the network panel."
    WRAPPER_CONSOLE_PROMPT="Press ENTER to close..."
    EXPAND_MSG1="Starting refugiOS disk auto-expansion..."
    EXPAND_MSG2="Expanding partition"
    EXPAND_MSG3="Resizing filesystem"
    EXPAND_MSG4="Disabling auto-expansion service..."
    EXPAND_MSG5="Auto-expansion completed successfully."
    EXPAND_SVC_DESC="refugiOS disk auto-expansion"
else
    REFUGIOS_LOCALE="es_ES.UTF-8"
    REFUGIOS_KBD="es"
    REFUGIOS_LANGUAGE="es"
    WELCOME_TITLE="¡Bienvenido a refugiOS!"
    WELCOME_BODY_START="Tu sistema se ha configurado correctamente en un"
    WELCOME_STEPS_LABEL="Pasos recomendados"
    WELCOME_STEP1="<b>Ajusta la resolución de pantalla si es necesario</b> en:\n   <i>Applications → Settings → Display</i>"
    WELCOME_STEP2="<b>Conéctate a una red WiFi o por cable de red</b>\n   (solo necesario durante la instalación)\n   Puedes configurar la red en:\n   <i>Applications → Settings → Advanced Network Configuration</i>"
    LAUNCHER_NAME="Completar instalación de refugiOS"
    WELCOME_STEP3="<b>Haz doble clic en el icono del escritorio</b>\n   «$LAUNCHER_NAME»\n   para finalizar la configuración del sistema."
    WELCOME_FOOTER="¡Disfruta de refugiOS!"
    LAUNCHER_COMMENT="Descarga e instala módulos desde GitHub"
    WRAPPER_PING="Comprobando conexión a Internet con github.com..."
    WRAPPER_OK="Conexión exitosa. Iniciando instalador..."
    WRAPPER_ERR_TITLE="Sin conexión a Internet - refugiOS"
    WRAPPER_ERR_TEXT="No se pudo conectar con github.com.\n\nPor favor, conéctate a una red WiFi o cableada\n(puedes usar el icono de red de NetworkManager en la bandeja de sistema)\nantes de intentar la instalación."
    WRAPPER_CONSOLE_ERR="ERROR: No hay conexión con github.com"
    WRAPPER_CONSOLE_TEXT1="Para completar la instalación, necesitas conexión a Internet."
    WRAPPER_CONSOLE_TEXT2="Por favor, conéctate a una red WiFi o cableada."
    WRAPPER_CONSOLE_TEXT3="Puedes usar 'nmtui' en terminal o el panel de red."
    WRAPPER_CONSOLE_PROMPT="Presiona ENTER para cerrar..."
    EXPAND_MSG1="Iniciando autoexpansión del disco de refugiOS..."
    EXPAND_MSG2="Expandiendo partición"
    EXPAND_MSG3="Redimensionando el sistema de archivos"
    EXPAND_MSG4="Deshabilitando servicio de autoexpansión..."
    EXPAND_MSG5="Autoexpansión completada con éxito."
    EXPAND_SVC_DESC="Autoexpansión del disco de refugiOS"
fi

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

echo "=> Iniciando la construcción de refugiOS (${REFUGIOS_LANG})..."

# 1. Instalar dependencias en el host (si faltan)
apt-get update
apt-get install -y debootstrap parted dosfstools e2fsprogs

# 2. Crear el archivo de imagen esparso (rápido)
echo "=> Creando imagen de ${IMG_SIZE}..."
truncate -s $IMG_SIZE $IMG_NAME

# 3. Particionar la imagen (GPT: BIOS Boot + EFI + Root)
echo "=> Particionando..."
parted -s $IMG_NAME mklabel gpt
parted -s $IMG_NAME mkpart BIOS_BOOT 1MiB 2MiB
parted -s $IMG_NAME set 1 bios_grub on
parted -s $IMG_NAME mkpart EFI fat32 2MiB 514MiB
parted -s $IMG_NAME set 2 esp on
parted -s $IMG_NAME mkpart ROOT ext4 514MiB 100%

# 4. Mapear la imagen a dispositivos loop
LOOP_DEV=$(losetup -Pf --show $IMG_NAME)
LOOP_EFI="${LOOP_DEV}p2"
LOOP_ROOT="${LOOP_DEV}p3"

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
set -x

# Forzar locale C durante toda la instalación para evitar warnings
export LC_ALL=C
export DEBIAN_FRONTEND=noninteractive

# Configurar repositorios
cat << 'SOURCES' > /etc/apt/sources.list
deb http://deb.debian.org/debian/ bookworm main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
deb http://deb.debian.org/debian/ bookworm-updates main contrib non-free non-free-firmware
SOURCES

apt-get update
apt-get install -y linux-image-amd64 linux-headers-amd64 build-essential \
                   grub-efi-amd64 grub-pc-bin sudo network-manager network-manager-gnome xfce4-goodies \
                   xfce4 xfce4-terminal curl cloud-guest-utils zenity lightdm \
                   epiphany-browser locales keyboard-configuration flatpak libglib2.0-bin \
                   firmware-iwlwifi firmware-brcm80211 firmware-atheros \
                   firmware-libertas firmware-misc-nonfree firmware-realtek \
                   firmware-amd-graphics xserver-xorg-video-amdgpu nvidia-driver

# Generar locale antes de configurarlo
sed -i "s/^# ${REFUGIOS_LOCALE}/${REFUGIOS_LOCALE}/" /etc/locale.gen
locale-gen
update-locale LANG=${REFUGIOS_LOCALE} LANGUAGE=${REFUGIOS_LANGUAGE}

# Preconfigurar teclado para evitar diálogos interactivos
debconf-set-selections << KBD_DEBCONF
keyboard-configuration keyboard-configuration/layoutcode string ${REFUGIOS_KBD}
keyboard-configuration keyboard-configuration/layout string ${REFUGIOS_KBD}
keyboard-configuration keyboard-configuration/variant select
keyboard-configuration keyboard-configuration/xkb-keymap select ${REFUGIOS_KBD}
KBD_DEBCONF

# Configurar teclado
cat > /etc/default/keyboard << KBD_CONF
XKBMODEL="pc105"
XKBLAYOUT="${REFUGIOS_KBD}"
XKBVARIANT=""
XKBOPTIONS=""
KBD_CONF

# Configurar idioma del entorno
cat > /etc/environment << ENV_CONF
LANG=${REFUGIOS_LOCALE}
LANGUAGE=${REFUGIOS_LANGUAGE}
ENV_CONF

# Crear un device.map temporal para mapear el loop device como hd0
mkdir -p /boot/grub
echo "(hd0) $LOOP_DEV" > /boot/grub/device.map

# Desactivar advertencias de os-prober en update-grub
if [ -f /etc/default/grub ]; then
    if ! grep -q "GRUB_DISABLE_OS_PROBER" /etc/default/grub; then
        echo "GRUB_DISABLE_OS_PROBER=true" >> /etc/default/grub
    fi
fi

# Configurar GRUB para arranque automático
cat << 'GRUB_DEFAULTS' >> /etc/default/grub
GRUB_TIMEOUT=1
GRUB_TIMEOUT_STYLE=menu
GRUB_DEFAULT=0
GRUB_CMDLINE_LINUX_DEFAULT="quiet"
GRUB_DISABLE_SUBMENU=y
GRUB_DEFAULTS

# Instalar GRUB para UEFI (medios removibles) sin registrar en NVRAM del host
grub-install --target=x86_64-efi --efi-directory=/boot/efi --removable --no-nvram

# Instalar GRUB para Legacy BIOS (arranque MBR en discos GPT)
grub-install --target=i386-pc $LOOP_DEV

update-grub

# Crear grub.cfg de fallback en la partición EFI para arranque UEFI fiable
mkdir -p /boot/efi/EFI/BOOT
echo "search --no-floppy --fs-uuid --set=root $UUID_ROOT" > /boot/efi/EFI/BOOT/grub.cfg
echo 'set prefix=(\$root)/boot/grub' >> /boot/efi/EFI/BOOT/grub.cfg
echo 'configfile /boot/grub/grub.cfg' >> /boot/efi/EFI/BOOT/grub.cfg

# Eliminar el device.map para que no quede en la imagen final
rm -f /boot/grub/device.map

# Configurar usuario por defecto (sin contraseña de login)
useradd -m -s /bin/bash $USER_NAME
passwd -d $USER_NAME
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

# Deshabilitar bloqueo de pantalla por inactividad en XFCE
mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml
cat << 'XFCE_SCREENLOCK' > /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-screensaver" version="1.0">
  <property name="saver" type="empty">
    <property name="mode" type="int" value="0"/>
    <property name="enabled" type="bool" value="false"/>
  </property>
  <property name="lock" type="empty">
    <property name="enabled" type="bool" value="false"/>
    <property name="with-screensaver" type="bool" value="false"/>
    <property name="fullscreen" type="bool" value="false"/>
  </property>
</channel>
XFCE_SCREENLOCK
chmod 644 /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml

# Inyectar Script de Autoexpansión Universal (NVMe/eMMC/SATA/loop)
cat << 'EXPAND_SCRIPT' > /usr/local/bin/refugios-expand.sh
#!/bin/bash
set -e
echo "=> $EXPAND_MSG1"
ROOT_PART=\$(findmnt -n -o SOURCE /)
PART_NAME=\$(basename "\$ROOT_PART")
PART_PATH=\$(readlink -f "/sys/class/block/\$PART_NAME")
DISK_NAME=\$(basename "\$(dirname "\$PART_PATH")")
DISK="/dev/\$DISK_NAME"
PART_NUM=\$(cat "/sys/class/block/\$PART_NAME/partition")

echo "$EXPAND_MSG2 \$PART_NUM en disco \$DISK..."
growpart "\$DISK" "\$PART_NUM" || [ \$? -eq 1 ]
echo "$EXPAND_MSG3 \$ROOT_PART..."
resize2fs "\$ROOT_PART"
echo "$EXPAND_MSG4"
systemctl disable refugios-expand.service
echo "=> $EXPAND_MSG5"
EXPAND_SCRIPT
chmod +x /usr/local/bin/refugios-expand.sh

# Inyectar Servicio de Autoexpansión
cat << 'EXPAND_SVC' > /etc/systemd/system/refugios-expand.service
[Unit]
Description=$EXPAND_SVC_DESC
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
LOG="/tmp/refugios-install.log"
echo "=== refugios-install-wrapper.sh iniciado: \$(date) ===" >> "\$LOG"
echo "=> $WRAPPER_PING"
if ping -c 1 -W 3 github.com >/dev/null 2>&1; then
    echo "=> $WRAPPER_OK"
    echo "Conexión OK, lanzando instalador..." >> "\$LOG"
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh 2>>"\$LOG" | bash
    echo "Instalador finalizado con código: \$?" >> "\$LOG"
else
    # Si hay sesión de X11 y zenity está instalado, mostrar cuadro de diálogo gráfico
    if [ -n "\$DISPLAY" ] && command -v zenity >/dev/null 2>&1; then
        zenity --error \\
               --title="$WRAPPER_ERR_TITLE" \\
               --text="$WRAPPER_ERR_TEXT" \\
               --width=450
    else
        echo ""
        echo "=========================================================="
        echo " $WRAPPER_CONSOLE_ERR"
        echo "=========================================================="
        echo " $WRAPPER_CONSOLE_TEXT1"
        echo " $WRAPPER_CONSOLE_TEXT2"
        echo " $WRAPPER_CONSOLE_TEXT3"
        echo "=========================================================="
        echo ""
        echo "$WRAPPER_CONSOLE_PROMPT"
        read
    fi
fi
echo "=== refugios-install-wrapper.sh finalizado ===" >> "\$LOG"
WRAPPER_SCRIPT
chmod +x /usr/local/bin/refugios-install-wrapper.sh

# Inyectar el lanzador del instalador en el Escritorio por defecto que llama al wrapper
mkdir -p /etc/skel/Desktop
cat << 'LAUNCHER' > /etc/skel/Desktop/Instalar_refugiOS.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=$LAUNCHER_NAME
Comment=$LAUNCHER_COMMENT
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

# Inyectar script de autostart para marcar todos los lanzadores como de confianza
cat << 'TRUST_SCRIPT' > /usr/local/bin/refugios-trust-launcher.sh
#!/bin/bash
# Esperar a que XFCE/GIO estén listos
sleep 5

trust_file() {
    [ ! -f "\$1" ] && return
    chmod +x "\$1"
    if command -v gio >/dev/null 2>&1; then
        CHECKSUM=\$(sha256sum "\$1" | awk '{print \$1}')
        gio set "\$1" metadata::xfce-exe-checksum "\$CHECKSUM" 2>/dev/null
    fi
}

DESK_DIR="\$HOME/Desktop"
[ -d "\$DESK_DIR" ] || DESK_DIR="\$HOME/Escritorio"
[ -d "\$DESK_DIR" ] || exit 0

for f in "\$DESK_DIR"/*.desktop; do
    trust_file "\$f"
done

# Vigilar archivos .desktop nuevos durante 60 segundos
if command -v inotifywait >/dev/null 2>&1; then
    timeout 60 inotifywait -q -m -e create --format '%w%f' "\$DESK_DIR" 2>/dev/null | while read -r newfile; do
        case "\$newfile" in *.desktop) trust_file "\$newfile" ;; esac
    done
fi
TRUST_SCRIPT
chmod +x /usr/local/bin/refugios-trust-launcher.sh

# Configurar el autostart para que ejecute el script de confianza al iniciar sesión
mkdir -p /etc/xdg/autostart
cat << 'TRUST_AUTOSTART' > /etc/xdg/autostart/refugios-desktop-trust.desktop
[Desktop Entry]
Type=Application
Name=Trust Desktop Launchers
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
LOG="/tmp/refugios-welcome.log"
echo "=== refugios-welcome.sh iniciado: \$(date) ===" >> "\$LOG"
echo "LANG=\$LANG LANGUAGE=\$LANGUAGE DISPLAY=\$DISPLAY" >> "\$LOG"

MARKER="\$HOME/.refugios-welcome-done"
if [ -f "\$MARKER" ]; then
    echo "Ya se ha mostrado el mensaje de bienvenida anteriormente." >> "\$LOG"
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

echo "DISK_SIZE_GB=\$DISK_SIZE_GB" >> "\$LOG"

WELCOME_TEXT="<b>$WELCOME_TITLE</b>\n\n$WELCOME_BODY_START <b>\${DISK_SIZE_GB} GB</b>.\n\n<b>$WELCOME_STEPS_LABEL:</b>\n\n1. $WELCOME_STEP1\n\n2. $WELCOME_STEP2\n\n3. $WELCOME_STEP3\n\n$WELCOME_FOOTER"
echo "WELCOME_TEXT=\$WELCOME_TEXT" >> "\$LOG"

zenity --info \\
       --title="$WELCOME_TITLE" \\
       --width=500 \\
       --text="\$WELCOME_TEXT" 2>>"\$LOG"

echo "zenity exit code: \$?" >> "\$LOG"
touch "\$MARKER"
echo "=== refugios-welcome.sh finalizado ===" >> "\$LOG"
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
echo "=> Log de construcción: $LOG_FILE"