#!/bin/bash
# Prepara una copia de una imagen ya construida para la prueba end-to-end del
# instalador: inyecta el repositorio local en /home/refugios/refugiOS-src y un
# autostart que abre el instalador al iniciar sesion. Asi el instalador se ejecuta
# en Developer Mode y prueba EL CODIGO LOCAL, no el publicado en GitHub.
#
#   tests/run_in_container.sh bash tests/prepare_e2e_image.sh IMAGEN_ORIGEN IMAGEN_DESTINO
set -euo pipefail

if [ "${REFUGIOS_IN_CONTAINER:-0}" != "1" ]; then
    echo "ERROR: ejecutalo con tests/run_in_container.sh"
    exit 1
fi

SRC="$1"
DST="$2"
REPO_DIR="/repo"
MNT="/mnt/refugios_e2e"
LOOP=""

cleanup() {
    if mountpoint -q "$MNT" 2>/dev/null; then umount "$MNT" || umount -lf "$MNT"; fi
    [ -n "$LOOP" ] && losetup -d "$LOOP" 2>/dev/null
    return 0
}
trap cleanup EXIT

echo "=> Copiando $SRC -> $DST"
cp --sparse=always "$SRC" "$DST"

LOOP=$(losetup -Pf --show "$DST")
mkdir -p "$MNT"
mount "${LOOP}p3" "$MNT"

echo "=> Inyectando el repositorio local en la imagen"
SRC_DIR="$MNT/home/refugios/refugiOS-src"
rm -rf "$SRC_DIR"
mkdir -p "$SRC_DIR/scripts" "$SRC_DIR/logo"
cp "$REPO_DIR/install.sh" "$REPO_DIR/install.py" "$REPO_DIR/i18n.py" "$SRC_DIR/"
cp "$REPO_DIR"/scripts/*.sh "$REPO_DIR"/scripts/*.py "$SRC_DIR/scripts/"
cp "$REPO_DIR"/logo/fondo.png "$SRC_DIR/logo/" 2>/dev/null || true
chmod +x "$SRC_DIR/install.sh" "$SRC_DIR"/scripts/*.sh
chown -R 1000:1000 "$SRC_DIR"

echo "=> Configurando el arranque automatico del instalador"
cat > "$MNT/etc/xdg/autostart/refugios-e2e-install.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=refugiOS E2E installer run
Exec=xfce4-terminal --maximize -e "bash /home/refugios/refugiOS-src/install.sh"
OnlyShowIn=XFCE;
StartupNotify=false
Terminal=false
EOF

# El popup de bienvenida taparia el instalador
rm -f "$MNT/etc/xdg/autostart/refugios-welcome.desktop"

sync
echo "=> Imagen E2E lista: $DST"
