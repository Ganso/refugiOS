#!/bin/bash
# Script de prueba local de arranque UEFI con QEMU para refugiOS

set -e

# Verificar compatibilidad del sistema operativo host
if [ ! -f /etc/os-release ]; then
    echo "ERROR: No se pudo determinar el sistema operativo."
    echo "Este script requiere un sistema Linux con QEMU y OVMF instalados."
    exit 1
fi
. /etc/os-release
SUPPORTED_DISTROS="Debian, Ubuntu, Linux Mint, Pop!_OS, Fedora, Arch Linux, Manjaro, openSUSE"
if [[ ! "$ID" =~ ^(debian|ubuntu|mint|pop|fedora|arch|manjaro|opensuse|endeavouros)$ ]] && \
   [[ ! "$ID_LIKE" =~ (debian|ubuntu|fedora|arch|suse) ]]; then
    echo "=========================================================="
    echo " ADVERTENCIA: Sistema operativo no verificado."
    echo "=========================================================="
    echo " Este script ha sido probado en: $SUPPORTED_DISTROS"
    echo " Sistema detectado: $NAME ($ID)"
    echo " Puedes continuar, pero podrían faltar dependencias."
    echo "=========================================================="
fi

# Determinar rutas relativas al script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# Permitir especificar el tamaño de la imagen o autodetectar una existente
IMG_SIZE="$1"
if [ -z "$IMG_SIZE" ]; then
    # Buscar cualquier imagen que coincida en el workspace
    EXISTING_IMG=$(find "$WORKSPACE_DIR" -maxdepth 1 -name "refugios-base-*.img" | head -n 1)
    if [ -n "$EXISTING_IMG" ]; then
        IMG_NAME="$EXISTING_IMG"
    else
        IMG_NAME="$WORKSPACE_DIR/refugios-base-16G-es.img"
    fi
else
    IMG_NAME="$WORKSPACE_DIR/refugios-base-${IMG_SIZE}.img"
fi

VARS_FILE="$WORKSPACE_DIR/refugios_vars.fd"

# Verificar que la imagen existe
if [ ! -f "$IMG_NAME" ]; then
    echo "ERROR: No se encontró la imagen $IMG_NAME."
    echo "Por favor, ejecute primero: sudo $SCRIPT_DIR/build_refugios.sh"
    exit 1
fi

# 1. Detectar archivos del firmware OVMF
echo "=> Detectando firmware OVMF (UEFI)..."
OVMF_CODE=""
OVMF_VARS_TEMPLATE=""

# Buscar en ubicaciones comunes de Debian/Ubuntu
if [ -f "/usr/share/OVMF/OVMF_CODE_4M.fd" ]; then
    OVMF_CODE="/usr/share/OVMF/OVMF_CODE_4M.fd"
    OVMF_VARS_TEMPLATE="/usr/share/OVMF/OVMF_VARS_4M.fd"
elif [ -f "/usr/share/OVMF/OVMF_CODE.fd" ]; then
    OVMF_CODE="/usr/share/OVMF/OVMF_CODE.fd"
    OVMF_VARS_TEMPLATE="/usr/share/OVMF/OVMF_VARS.fd"
elif [ -f "/usr/share/ovmf/OVMF.fd" ]; then
    # En algunos sistemas antiguos, hay un solo archivo monolítico o se ubica en minúsculas
    OVMF_CODE="/usr/share/ovmf/OVMF.fd"
# Fedora: paquete edk2-ovmf
elif [ -f "/usr/share/edk2/ovmf/OVMF_CODE.fd" ]; then
    OVMF_CODE="/usr/share/edk2/ovmf/OVMF_CODE.fd"
    OVMF_VARS_TEMPLATE="/usr/share/edk2/ovmf/OVMF_VARS.fd"
# Arch Linux: paquete edk2-ovmf
elif [ -f "/usr/share/edk2/x64/OVMF_CODE.4m.fd" ]; then
    OVMF_CODE="/usr/share/edk2/x64/OVMF_CODE.4m.fd"
    OVMF_VARS_TEMPLATE="/usr/share/edk2/x64/OVMF_VARS.4m.fd"
elif [ -f "/usr/share/edk2/x64/OVMF_CODE.fd" ]; then
    OVMF_CODE="/usr/share/edk2/x64/OVMF_CODE.fd"
    OVMF_VARS_TEMPLATE="/usr/share/edk2/x64/OVMF_VARS.fd"
fi

if [ -z "$OVMF_CODE" ]; then
    echo "ERROR: No se encontró el firmware OVMF UEFI."
    echo "Por favor, instala OVMF en tu distribución:"
    echo "  Debian/Ubuntu:  sudo apt install ovmf qemu-system-x86"
    echo "  Fedora:         sudo dnf install edk2-ovmf qemu-system-x86-core"
    echo "  Arch Linux:     sudo pacman -S edk2-ovmf qemu-system-x86"
    exit 1
fi

echo "   OVMF Code: $OVMF_CODE"
if [ -n "$OVMF_VARS_TEMPLATE" ]; then
    echo "   OVMF Vars: $OVMF_VARS_TEMPLATE"
    # Crear copia local escribible de las variables UEFI
    if [ ! -f "$VARS_FILE" ]; then
        echo "=> Creando copia local de variables UEFI ($VARS_FILE)..."
        cp "$OVMF_VARS_TEMPLATE" "$VARS_FILE"
    fi
fi

# 2. Comprobar soporte de aceleración por hardware (KVM)
KVM_ARGS=""
if [ -w /dev/kvm ]; then
    echo "=> Aceleración KVM habilitada y con permisos de escritura."
    KVM_ARGS="-enable-kvm -cpu host"
else
    echo "=> ADVERTENCIA: KVM no está habilitado o no tienes permisos en /dev/kvm."
    echo "   El arranque puede ser extremadamente lento."
fi

# 3. Lanzar QEMU
echo "=> Lanzando QEMU con la imagen de refugiOS..."
# Estructuramos los argumentos de QEMU
QEMU_CMD=(
    qemu-system-x86_64
    $KVM_ARGS
    -m 2G
    -smp 2
    -drive file="$IMG_NAME",format=raw,index=0,media=disk
    -vga virtio
    -net nic -net user
)

# Añadir flash de firmware UEFI según el tipo detectado
if [ -n "$OVMF_VARS_TEMPLATE" ]; then
    QEMU_CMD+=(
        -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE"
        -drive if=pflash,format=raw,file="$VARS_FILE"
    )
else
    QEMU_CMD+=(
        -bios "$OVMF_CODE"
    )
fi

echo "Ejecutando: ${QEMU_CMD[*]}"
"${QEMU_CMD[@]}"
