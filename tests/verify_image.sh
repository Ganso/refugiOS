#!/bin/bash
# Verifica una imagen base ya construida ANTES de publicarla.
#
#   tests/verify_image.sh IMAGEN [--expand]
#
# Sin --expand comprueba el contenido y la integridad (segundos).
# Con --expand comprueba ademas que la particion crece al tamano real del
# dispositivo, arrancando una copia sobre un disco de 128 GB (unos 5 minutos).
#
# Por que existe: la version 0.23 se publico sin el servicio de autoexpansion
# habilitado y arranco perfectamente en todas las pruebas. El build termino con
# codigo 0, su log registraba el enlace como creado, y la captura de pantalla
# mostraba un escritorio correcto. Ninguna de esas senales mira lo que de verdad
# hay dentro de la imagen, y la expansion no se puede ejercitar en un disco del
# mismo tamano que la imagen. Este script comprueba el artefacto, no el proceso.
set -uo pipefail

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$TESTS_DIR")"
CONTAINER="refugios-test:trixie"

IMAGE="${1:-}"
MODE="${2:-}"

if [ -z "$IMAGE" ] || [ ! -f "$IMAGE" ]; then
    echo "Uso: tests/verify_image.sh IMAGEN [--expand]"
    exit 1
fi
IMAGE="$(readlink -f "$IMAGE")"
IMG_DIR="$(dirname "$IMAGE")"
IMG_NAME="$(basename "$IMAGE")"
FAILED=0

check() {
    if [ "$1" == "0" ]; then
        echo "   [OK]   $2"
    else
        echo "   [FALLO] $2"
        FAILED=1
    fi
}

if ! docker image inspect "$CONTAINER" >/dev/null 2>&1; then
    docker build -q -t "$CONTAINER" "$TESTS_DIR/docker" >/dev/null
fi

# ============================================================================
# 1. Integridad y contenido
# ============================================================================
echo "=> Verificando $IMG_NAME"

# -i es imprescindible: sin el, docker no conecta la entrada estandar, el script
# de dentro no llega a ejecutarse y la comprobacion devuelve un OK enganoso.
docker run --rm -i --privileged -v "$IMG_DIR:/out" -v /dev:/dev "$CONTAINER" bash -s "$IMG_NAME" <<'DENTRO'
set -uo pipefail
IMG="/out/$1"
FALLOS=0

LOOP=$(losetup -Pf --show "$IMG")
trap 'losetup -d "$LOOP" 2>/dev/null' EXIT

echo "-- integridad del sistema de ficheros --"
SALIDA=$(e2fsck -fn "${LOOP}p3" 2>&1)
if grep -q "WARNING: Filesystem still has errors" <<<"$SALIDA"; then
    echo "   [FALLO] el sistema de ficheros tiene errores: no publicar"
    grep -E "differences|Free|checksum" <<<"$SALIDA" | head -6
    FALLOS=1
else
    echo "   [OK]   sistema de ficheros limpio"
fi

echo "-- artefactos que debe contener la imagen --"
mkdir -p /mnt/v && mount -o ro "${LOOP}p3" /mnt/v
for a in /usr/local/bin/refugios-expand.sh \
         /etc/systemd/system/refugios-expand.service \
         /etc/systemd/system/multi-user.target.wants/refugios-expand.service \
         /usr/local/bin/refugios-install-wrapper.sh \
         /usr/local/bin/refugios-trust-launcher.sh \
         /usr/local/bin/refugios-welcome.sh \
         /etc/xdg/autostart/refugios-desktop-trust.desktop \
         /etc/xdg/autostart/refugios-welcome.desktop \
         /etc/skel/Desktop/Instalar_refugiOS.desktop \
         /home/refugios/Desktop/Instalar_refugiOS.desktop \
         /etc/fstab /etc/hostname /boot/grub/grub.cfg; do
    if [ -e "/mnt/v$a" ] || [ -L "/mnt/v$a" ]; then
        echo "   [OK]   $a"
    else
        echo "   [FALLO] $a"
        FALLOS=1
    fi
done
umount /mnt/v
exit $FALLOS
DENTRO
check $? "contenido e integridad"

# ============================================================================
# 2. Expansion del disco (opcional: tarda unos minutos)
# ============================================================================
if [ "$MODE" == "--expand" ]; then
    echo
    echo "=> Comprobando la autoexpansion en un disco de 128 GB"
    BIG="$IMG_DIR/.verify-128g.img"
    rm -f "$BIG"
    truncate -s 123009761280 "$BIG"
    dd if="$IMAGE" of="$BIG" bs=4M conv=notrunc,sparse status=none
    check $? "copia volcada sobre el disco grande"

    python3 "$TESTS_DIR/qemu_boot_check.py" "$BIG" --shots 150 \
        --out "$TESTS_DIR/out" --prefix verify_expand >/dev/null 2>&1
    check $? "arranque completado"

    # El mensaje de bienvenida NO sirve como prueba: informa del tamano del disco,
    # no del de la particion, asi que dice 114 GB tambien cuando la expansion falla.
    SECTORES=$(docker run --rm --privileged -v "$IMG_DIR:/out" -v /dev:/dev "$CONTAINER" \
        bash -c 'L=$(losetup -Pf --show /out/.verify-128g.img); sfdisk -l "$L" 2>/dev/null | awk "/p3/ {print \$4}"; losetup -d "$L"')
    echo "   sectores de la particion raiz: ${SECTORES:-desconocido}"
    [ -n "$SECTORES" ] && [ "$SECTORES" -gt 200000000 ]
    check $? "la particion raiz ocupa el disco entero (>100 GB)"

    rm -f "$BIG"
fi

echo
if [ "$FAILED" -eq 0 ]; then
    echo "=> $IMG_NAME: LISTA PARA PUBLICAR"
else
    echo "=> $IMG_NAME: NO PUBLICAR, hay comprobaciones fallidas"
fi
exit $FAILED
