#!/bin/bash
# Tests de scripts/build_refugios.sh (C1, C2).
#
# Comprueba, con una construccion real pero abortada nada mas entrar en el chroot
# (para que dure unos minutos en lugar de media hora):
#   C1 - un fallo dentro del chroot detiene el build y devuelve codigo != 0
#   C2 - la imagen previa se descarta en lugar de reutilizarse
#   C2 - un montaje residual de un build anterior no se apila
#
# Debe ejecutarse dentro del contenedor privilegiado:
#   tests/run_in_container.sh bash tests/test_build.sh
set -uo pipefail

if [ "${REFUGIOS_IN_CONTAINER:-0}" != "1" ]; then
    echo "ERROR: ejecutalo con tests/run_in_container.sh bash tests/test_build.sh"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="/tmp/refugios_build_test"
MNT_DIR="/mnt/refugios_build"
FAILED=0

check() {
    if [ "$1" == "0" ]; then
        echo "   [OK]   $2"
    else
        echo "   [FAIL] $2"
        FAILED=1
    fi
}

rm -rf "$WORK"
mkdir -p "$WORK/scripts"

# Copia instrumentada: falla nada mas entrar en el chroot
sed 's|^set -x$|set -x\nfalse # INYECTADO POR EL TEST|' \
    "$REPO_DIR/scripts/build_refugios.sh" > "$WORK/scripts/build_refugios.sh"
chmod +x "$WORK/scripts/build_refugios.sh"
grep -q "INYECTADO POR EL TEST" "$WORK/scripts/build_refugios.sh"
check $? "el fallo de prueba se ha inyectado en el heredoc del chroot"

# C2: imagen previa con contenido reconocible (0xFF) que NO debe sobrevivir
IMG="$WORK/refugios-base-2G-es.img"
head -c 4194304 /dev/zero | tr '\0' '\377' > "$IMG"
truncate -s 2G "$IMG"

# C2: montaje residual de un build anterior
mkdir -p "$MNT_DIR"
umount -lf "$MNT_DIR" 2>/dev/null
mount -t tmpfs tmpfs "$MNT_DIR"
check $? "preparado un montaje residual en $MNT_DIR"

echo "=> Ejecutando el build instrumentado (debootstrap incluido, unos minutos)..."
cd "$WORK"
./scripts/build_refugios.sh -s 2G -l es > "$WORK/build.log" 2>&1
STATUS=$?

# C1: el build debe fallar de forma explicita
[ "$STATUS" -ne 0 ]
check $? "C1: el build termina con codigo != 0 (obtenido: $STATUS)"

grep -q "La configuración dentro del chroot falló" "$WORK/build.log"
check $? "C1: se informa del fallo del chroot con un mensaje explicito"

# C2: la imagen se ha recreado desde cero (sin el patron 0xFF inicial)
if [ -f "$IMG" ]; then
    FF_COUNT=$(head -c 1048576 "$IMG" | tr -d '\377' | wc -c)
    [ "$FF_COUNT" -gt 0 ]
    check $? "C2: la imagen previa se descarto en lugar de reutilizarse"
else
    check 1 "C2: la imagen no existe tras el build"
fi

# C2: no deben quedar montajes apilados
STACKED=$(findmnt -n "$MNT_DIR" 2>/dev/null | wc -l)
[ "$STACKED" -le 1 ]
check $? "C2: no quedan montajes apilados en $MNT_DIR (encontrados: $STACKED)"

# Limpieza
while mountpoint -q "$MNT_DIR" 2>/dev/null; do umount -lf "$MNT_DIR" || break; done
rm -rf "$WORK"

if [ "$FAILED" -eq 0 ]; then
    echo "=> test_build.sh: TODO CORRECTO"
else
    echo "=> test_build.sh: HAY FALLOS"
fi
exit $FAILED
