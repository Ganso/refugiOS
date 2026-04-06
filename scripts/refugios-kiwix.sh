#!/bin/bash
# ============================================
# refugiOS - Lanzador de Recursos Kiwix
# Abre un archivo ZIM con Kiwix Desktop
# ============================================

ZIM_FILE="$1"

if [ -z "$ZIM_FILE" ]; then
    echo "Uso: refugios-kiwix.sh <ruta_al_archivo.zim>"
    exit 1
fi

# Detectar el ejecutable de Kiwix disponible
if command -v kiwix-desktop &>/dev/null; then
    KIWIX_BIN="kiwix-desktop"
elif [ -f "$HOME/refugiOS/Apps/kiwix-desktop.appimage" ]; then
    KIWIX_BIN="$HOME/refugiOS/Apps/kiwix-desktop.appimage"
else
    # Fallback: buscar cualquier AppImage de kiwix en la carpeta de Apps
    KIWIX_BIN=$(find "$HOME/refugiOS/Apps" -name "kiwix-desktop*.appimage" 2>/dev/null | sort | tail -1)
fi

if [ -z "$KIWIX_BIN" ]; then
    echo "Error: No se encontró Kiwix Desktop instalado."
    exit 1
fi

exec "$KIWIX_BIN" "$ZIM_FILE"
