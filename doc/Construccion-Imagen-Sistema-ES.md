# Guía de Construcción de Imagen de Sistema refugiOS

Esta guía detalla el proceso automatizado para generar una **imagen de disco base de refugiOS** desde cero, sin depender de una ISO de Xubuntu preexistente. El sistema resultante es una instalación nativa de Debian Trixie con escritorio XFCE, lista para ser volcada directamente a un pendrive USB o dispositivo externo.

A diferencia del método tradicional basado en una ISO Live de Xubuntu con persistencia, esta imagen produce un **sistema instalado nativamente**, lo que elimina las capas de indirección del modo Live y ofrece mejor rendimiento, menor desgaste del dispositivo y mayor control sobre la configuración base.

> [!TIP]
> **Método más rápido:** Si no necesitas personalizar la imagen base, puedes descargar la imagen pregenerada directamente desde [refugios.ganso.org](https://refugios.ganso.org/refugios-base-16G-es.img) y saltarte todo este proceso. Solo tienes que grabarla en un USB y arrancar. Consulta el **[README](../README.md)** para los pasos de inicio rápido.

> [!IMPORTANT]
> Este método está pensado para **usuarios avanzados** que deseen construir la imagen desde su origen o preparar múltiples unidades idénticas de forma eficiente.

> [!NOTE]
> La elección del dispositivo físico donde volcarás la imagen (SSD, pendrive, adaptador SATA) condiciona el rendimiento y la vida útil de tu refugiOS. Consulta la **[Guía de Elección del Medio de Instalación](Eleccion-Medio-Instalacion-ES.md)** antes de empezar.

Para probar la imagen generada en una máquina virtual antes de grabarla en un USB, consulta la **[Guía de Virtualización](Guia-Virtualizacion-y-Pendrive-ES.md)**.

---

## 1. Requisitos Previos

### 1.1. Sistema Operativo del Host

El script de construcción requiere un sistema operativo **basado en Debian** (Debian, Ubuntu, Linux Mint, Pop!_OS). Si tu distribución no está basada en Debian, el script mostrará un error y se detendrá.

El sistema debe ser de **arquitectura x86_64 (amd64)**.

### 1.2. Permisos de Root

El script debe ejecutarse como **root** (mediante `sudo`), ya que necesita:
- Crear y particionar imágenes de disco
- Montar sistemas de archivos
- Ejecutar `debootstrap`
- Configurar dispositivos loop
- Instalar GRUB en la imagen

### 1.3. Dependencias

El script instala automáticamente las dependencias necesarias si no están presentes:
- `debootstrap` — Para crear el sistema base Debian desde cero
- `parted` — Para particionar la imagen (GPT)
- `dosfstools` — Para formatear la partición EFI (FAT32)
- `e2fsprogs` — Para formatear la partición raíz (ext4)

Para el script de pruebas (`test_boot.sh`), necesitarás además:
- `qemu-system-x86` — Emulador/QEMU para probar el arranque
- `ovmf` — Firmware UEFI para QEMU

Instalación de las dependencias de prueba:

| Distribución | Comando de instalación |
| :--- | :--- |
| **Debian / Ubuntu** | `sudo apt install ovmf qemu-system-x86` |
| **Fedora** | `sudo dnf install edk2-ovmf qemu-system-x86-core` |
| **Arch Linux** | `sudo pacman -S edk2-ovmf qemu-system-x86` |

> [!NOTE]
> El script `build_refugios.sh` solo es compatible con sistemas basados en Debian. Sin embargo, `test_boot.sh` es compatible con un rango más amplio de distribuciones (Debian, Ubuntu, Mint, Pop!_OS, Fedora, Arch, Manjaro, openSUSE), ya que solo necesita QEMU y OVMF.

### 1.4. Espacio en Disco

La imagen generada es un **archivo disperso (sparse)**: se crea al tamaño solicitado pero solo ocupa el espacio real de los datos escritos. Una imagen de 16G recién creada ocupará aproximadamente **7-8 GB** en disco. Asegúrate de tener al menos **10 GB libres** antes de comenzar.

---

## 2. Construcción de la Imagen Base

### 2.1. Ejecución del Script

```bash
sudo bash scripts/build_refugios.sh [TAMAÑO]
```

El parámetro `TAMAÑO` es opcional y define el tamaño virtual de la imagen. Por defecto es **16G**. El formato debe ser un número seguido de `G` (gigabytes), `M` (megabytes) o `K` (kilobytes).

Ejemplos:

| Comando | Tamaño de la imagen | Nombre del archivo generado |
| :--- | :--- | :--- |
| `sudo bash scripts/build_refugios.sh` | 16 GB (por defecto) | `refugios-base-16G.img` |
| `sudo bash scripts/build_refugios.sh 32G` | 32 GB | `refugios-base-32G.img` |
| `sudo bash scripts/build_refugios.sh 64G` | 64 GB | `refugios-base-64G.img` |
| `sudo bash scripts/build_refugios.sh 500M` | 500 MB | `refugios-base-500M.img` |

> [!WARNING]
> El tamaño de la imagen debe coincidir con (o ser ligeramente inferior al) tamaño real del dispositivo USB donde la vas a grabar. Los fabricantes suelen anunciar capacidades ligeramente superiores a las reales. Se recomienda dejar un margen de seguridad.

### 2.2. Proceso Interno del Script

El script ejecuta automáticamente los siguientes pasos:

1. **Validación del entorno:** Comprueba que el host es Debian-based, que se ejecuta como root y que el tamaño es válido.
2. **Instalación de dependencias:** Ejecuta `apt-get update` e instala `debootstrap`, `parted`, `dosfstools` y `e2fsprogs` si faltan.
3. **Creación de la imagen dispersa:** Usa `truncate -s` para crear el archivo `.img` del tamaño indicado.
4. **Particionado GPT:** Crea dos particiones:
   - **Partición 1 (EFI):** FAT32, de 1 MiB a 513 MiB, marcada como ESP (EFI System Partition).
   - **Partición 2 (ROOT):** ext4, de 513 MiB al final del disco.
5. **Mapeo con loop devices:** Asocia la imagen a un dispositivo loop con `losetup -Pf` para acceder a las particiones.
6. **Formateo:** Formatea EFI como FAT32 y ROOT como ext4. Obtiene los UUIDs de ambas particiones.
7. **Montaje:** Monta la partición raíz en `/mnt/refugios_build` y la EFI en `/mnt/refugios_build/boot/efi`.
8. **Debootstrap:** Instala el sistema base Debian Trixie (amd64) desde los repositorios oficiales.
9. **Generación de fstab:** Crea `/etc/fstab` con los UUIDs reales de las particiones para asegurar el montaje correcto en arranque.
10. **Configuración dentro del chroot:** Monta `/dev`, `/dev/pts`, `/proc`, `/sys` y `/run` dentro de la imagen y ejecuta todos los pasos de configuración en un entorno chroot (ver sección 2.3).
11. **Desmontaje y limpieza:** Desmonta todo en orden inverso y elimina el dispositivo loop.

### 2.3. Configuración dentro del Chroot

Dentro del entorno chroot, el script realiza la siguiente configuración:

#### Sistema Base
- Configura los repositorios APT de Debian Trixie (main, contrib, non-free, non-free-firmware) incluyendo security y updates.
- Instala los paquetes esenciales:
  - **Kernel:** `linux-image-amd64`
  - **Bootloader:** `grub-efi-amd64`
  - **Sistema:** `sudo`, `network-manager`
  - **Escritorio:** `xfce4`, `xfce4-terminal`, `lightdm`
  - **Herramientas:** `curl`, `cloud-guest-utils`, `zenity`
  - **Navegador:** `epiphany-browser`
- Instala GRUB en modo **removible** (`--removable --no-nvram`), lo que es vital para que el sistema arranque desde un pendrive USB sin necesidad de registrar la entrada en la NVRAM del host.
- Desactiva `os-prober` en GRUB para evitar advertencias innecesarias.
- Genera la configuración de GRUB con `update-grub`.

#### Usuario por Defecto
- Crea el usuario `refugios` con contraseña `refugios`.
- Añade el usuario al grupo `sudo`.
- Configura **sudo sin contraseña** para el usuario `refugios` (`/etc/sudoers.d/refugios`).
- Configura **autologin** en LightDM para que el escritorio se cargue automáticamente sin pedir credenciales.

#### Red y Hostname
- Hostname: `refugios`
- Configura `/etc/hosts` con las entradas estándar para localhost e IPv6.

#### Autoexpansión del Disco
- Inyecta el script `/usr/local/bin/refugios-expand.sh` que:
  - Detecta automáticamente el disco y partición raíz (compatible con NVMe, eMMC, SATA y loop).
  - Expande la partición con `growpart`.
  - Redimensiona el sistema de archivos con `resize2fs`.
  - Se **deshabilita automáticamente** tras ejecutarse correctamente.
- Crea el servicio systemd `refugios-expand.service` que ejecuta la expansión en el primer arranque.

#### Lanzador del Instalador en el Escritorio
- Inyecta `/usr/local/bin/refugios-install-wrapper.sh`, un wrapper que:
  - Comprueba la conexión a Internet haciendo ping a `github.com`.
  - Si hay conexión, descarga y ejecuta el instalador oficial de refugiOS.
  - Si no hay conexión, muestra un cuadro de diálogo gráfico (zenity) o un mensaje en terminal indicando que se necesita Internet.
- Crea el lanzador de escritorio `/etc/skel/Desktop/Instalar_refugiOS.desktop` que ejecuta el wrapper desde `xfce4-terminal`.
- Copia el lanzador al escritorio del usuario `refugios`.

#### Personalización del Escritorio XFCE
- Oculta los iconos por defecto del escritorio (Home, Papelera, Sistema de archivos, Dispositivos extraíbles) mediante configuración XML de XFCE.

#### Bienvenida al Primer Arranque
- Inyecta `/usr/local/bin/refugios-welcome.sh`, un script que:
  - Detecta el tamaño real del disco de arranque.
  - Muestra un cuadro de diálogo zenity de bienvenida con la información del disco y los pasos recomendados (ajustar resolución, lanzar el instalador).
  - Se **autoelimina** tras ejecutarse una vez (marca `$HOME/.refugios-welcome-done`).

---

## 3. Prueba de Arranque

Una vez generada la imagen, puedes verificar que arranca correctamente antes de volcarla a un dispositivo físico. Para instrucciones completas con QEMU, VirtualBox y otros métodos, consulta la **[Guía de Virtualización](Guia-Virtualizacion-y-Pendrive-ES.md)**.

### 3.1. Script Automatizado de Prueba

```bash
bash scripts/test_boot.sh [TAMAÑO]
```

El parámetro `TAMAÑO` es opcional. Si no se especifica, el script busca automáticamente cualquier imagen `refugios-base-*.img` en el directorio raíz del proyecto.

Ejemplos:

| Comando | Comportamiento |
| :--- | :--- |
| `bash scripts/test_boot.sh` | Busca y usa la primera imagen `refugios-base-*.img` que encuentre |
| `bash scripts/test_boot.sh 16G` | Usa la imagen `refugios-base-16G.img` |

> [!NOTE]
> A diferencia del script de construcción, `test_boot.sh` **no requiere permisos de root** (salvo que `/dev/kvm` necesite permisos especiales para la aceleración KVM).

### 3.2. Proceso Interno del Script de Prueba

1. **Detección del firmware OVMF:** Busca automáticamente los archivos de firmware UEFI (OVMF) en las rutas estándar de cada distribución:
   - Debian/Ubuntu: `/usr/share/OVMF/`
   - Fedora: `/usr/share/edk2/ovmf/`
   - Arch Linux: `/usr/share/edk2/x64/`
2. **Copia de variables UEFI:** Si se encuentran archivos separados de código y variables OVMF, crea una copia local escribible (`refugios_vars.fd`) para que QEMU pueda modificar las variables de arranque UEFI.
3. **Detección de KVM:** Comprueba si la aceleración KVM está disponible (`/dev/kvm`). Si está disponible, la habilita para un arranque rápido; si no, advierte de que el arranque será extremadamente lento.
4. **Lanzamiento de QEMU:** Ejecuta QEMU con los siguientes parámetros:
   - **RAM:** 2 GB
   - **CPUs:** 2
   - **Disco:** La imagen raw generada
   - **VGA:** virtio
   - **Red:** Emulación de red con NAT (nic/user)
   - **Firmware UEFI:** Detectado automáticamente (pflash o bios según el formato disponible)

### 3.3. Dentro de la Máquina Virtual

Al arrancar la imagen en QEMU verás:

1. El cargador GRUB con la entrada de refugiOS.
2. LightDM iniciando sesión automáticamente como el usuario `refugios`.
3. El escritorio XFCE con:
   - Los iconos por defecto del escritorio ocultos.
   - El lanzador **"Completar instalación de refugiOS"** en el escritorio.
   - El popup de bienvenida mostrando el tamaño del disco y los pasos recomendados.

Para completar la instalación, conecta la red virtual de QEMU (ya habilitada por defecto con NAT) y haz doble clic en el lanzador del escritorio, o ejecuta en la terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

---

## 4. Volcado al Dispositivo Físico

Una vez que la imagen ha sido verificada en QEMU, puedes volcarla a tu pendrive o disco externo:

```bash
# ¡ASEGÚRATE de que /dev/sdX es tu USB real con 'lsblk'!
sudo dd if=refugios-base-16G.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

> [!WARNING]
> Verifica siempre con `lsblk` o `fdisk -l` cuál es el dispositivo real de tu USB antes de ejecutar `dd`. Escribir en el disco equivocado destruirá todos los datos de ese disco.

Tras el volcado, el dispositivo arrancará automáticamente en UEFI en cualquier PC compatible. En el primer arranque:

1. El servicio de **autoexpansión** redimensionará la partición raíz para ocupar todo el espacio disponible del disco real.
2. Se mostrará el **popup de bienvenida** con las instrucciones básicas.
3. Podrás lanzar el **instalador de refugiOS** desde el icono del escritorio.

---

## 5. Estructura de Particiones de la Imagen

La imagen generada tiene el siguiente esquema de particionado GPT:

| Partición | Tamaño | Tipo | Formato | Punto de montaje | Etiqueta/Flags |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 (EFI) | 512 MiB | EFI System Partition | FAT32 | `/boot/efi` | ESP (bootable) |
| 2 (ROOT) | Resto del disco | Linux filesystem | ext4 | `/` | - |

El archivo `/etc/fstab` se genera automáticamente con los UUIDs reales de ambas particiones para garantizar el montaje correcto en cualquier dispositivo.

---

## 6. Scripts y Servicios Inyectados en la Imagen

El script de construcción inyecta los siguientes componentes en la imagen final:

| Ruta | Tipo | Descripción |
| :--- | :--- | :--- |
| `/usr/local/bin/refugios-expand.sh` | Script | Autoexpansión del disco en el primer arranque |
| `/etc/systemd/system/refugios-expand.service` | Servicio systemd | Ejecuta la autoexpansión y se deshabilita automáticamente |
| `/usr/local/bin/refugios-install-wrapper.sh` | Script | Wrapper del instalador con comprobación de conectividad |
| `/etc/skel/Desktop/Instalar_refugiOS.desktop` | Lanzador .desktop | Icono del instalador en el escritorio |
| `/usr/local/bin/refugios-trust-launcher.sh` | Script | Marca los lanzadores como fiables vía GIO |
| `/etc/xdg/autostart/refugios-desktop-trust.desktop` | Autostart | Ejecuta el script de confianza al iniciar sesión |
| `/usr/local/bin/refugios-welcome.sh` | Script | Popup de bienvenida en el primer arranque |
| `/etc/xdg/autostart/refugios-welcome.desktop` | Autostart | Ejecuta el popup de bienvenida al iniciar sesión |
| `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml` | Config XFCE | Oculta iconos por defecto del escritorio |
| `/etc/lightdm/lightdm.conf.d/autologin.conf` | Config LightDM | Autologin para el usuario `refugios` |
| `/etc/sudoers.d/refugios` | Config sudo | Sudo sin contraseña para el usuario `refugios` |

---

## 7. Certificación de Iconos de Escritorio

> [!NOTE]
> Los iconos del escritorio (lanzadores `.desktop`) se marcan ahora **automáticamente como fiables** por XFCE en el primer inicio de sesión. No se requiere intervención manual.

### Cómo Funciona

El script de construcción incluye `libglib2.0-bin` en el sistema base, que proporciona el comando `gio`. Al iniciar sesión, el script de autostart `refugios-trust-launcher.sh`:

1. Otorga permisos de ejecución a cada lanzador (`chmod +x`).
2. Calcula el checksum SHA-256 del archivo y lo almacena en los metadatos GIO (`metadata::xfce-exe-checksum`).

Este es el único campo de metadatos que XFCE verifica para considerar un archivo `.desktop` como fiable. El instalador (`install.py`) aplica el mismo mecanismo a cualquier icono nuevo que cree.

---

## 8. Comparativa: Imagen Nativa vs. ISO Live con Persistencia

| Aspecto | Imagen Nativa (este método) | ISO Live con Persistencia |
| :--- | :--- | :--- |
| **Base del sistema** | Debian Trixie nativo | XUbuntu Live (SquashFS) |
| **Rendimiento** | Superior (sistema instalado directamente) | Inferior (capa de indirección SquashFS) |
| **Desgaste del USB** | Menor (sin overlay de escritura continua) | Mayor (escritura constante en partición writable) |
| **Espacio ocupado (base)** | ~7-8 GB | ~2-3 GB (ISO comprimida) |
| **Personalización** | Completa (sistema real instalado) | Limitada (solo capa de persistencia) |
| **Complejidad de creación** | Media (un comando automatizado) | Baja (Rufus/mkusb con ISO existente) |
| **Requisitos del host** | Debian-based + root | Cualquier SO con Rufus/mkusb |
| **Autologin** | Sí (configurado por defecto) | Sí (propio del modo Live) |
| **Autoexpansión** | Sí (systemd, primer arranque) | No (tamaño fijo de la imagen) |

---

## 9. Flujos de Trabajo Recomendados

### Flujo A: Preparar una única unidad USB

1. Construye la imagen: `sudo bash scripts/build_refugios.sh 64G`
2. Prueba el arranque en una máquina virtual: consulta la **[Guía de Virtualización](Guia-Virtualizacion-y-Pendrive-ES.md)** o usa el script rápido: `bash scripts/test_boot.sh 64G`
3. Si arranca correctamente, vuelca al USB: `sudo dd if=refugios-base-64G.img of=/dev/sdX bs=4M status=progress conv=fsync`
4. Arranca desde el USB y completa la instalación.

### Flujo B: Preparar múltiples unidades idénticas

1. Construye la imagen una vez: `sudo bash scripts/build_refugios.sh 16G`
2. Prueba el arranque: `bash scripts/test_boot.sh`
3. Vuelca la misma imagen a todos los USBs:
   ```bash
   for dev in /dev/sdX /dev/sdY /dev/sdZ; do
       sudo dd if=refugios-base-16G.img of=$dev bs=4M status=progress conv=fsync
   done
   ```
4. Cada unidad se autoexpandirá en su primer arranque.

> [!TIP]
> Para preparar lotes grandes de dispositivos, consulta también la **[Guía de Clonado de Unidades](Clonado-de-Pendrive-ES.md)** para métodos más eficientes como el uso de `clonezilla` o duplicadores de hardware.

---

[Volver a la documentación](../README.md)
