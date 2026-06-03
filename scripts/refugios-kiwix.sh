#!/bin/bash
# ============================================
# refugiOS - Kiwix Resource Launcher
# Opens a ZIM file with Kiwix Desktop
# ============================================

ZIM_FILE="$1"
SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

if [ -z "$ZIM_FILE" ]; then
    echo "Usage: refugios-kiwix.sh <path_to_zim_file>"
    exit 1
fi

# Resolve symlinks to real paths (Flatpak sandbox can't follow symlinks properly)
if [ -L "$ZIM_FILE" ]; then
    ZIM_FILE=$(readlink -f "$ZIM_FILE")
fi

if [ ! -f "$ZIM_FILE" ]; then
    echo "$(t error): ZIM file not found: $ZIM_FILE"
    exit 1
fi

# Detect available Kiwix executable
if command -v kiwix-desktop &>/dev/null; then
    KIWIX_BIN="kiwix-desktop"
elif [ -f "$HOME/refugiOS/Apps/kiwix-desktop.appimage" ]; then
    KIWIX_BIN="$HOME/refugiOS/Apps/kiwix-desktop.appimage"
    export APPIMAGE_EXTRACT_AND_RUN=1
elif flatpak list --app | grep -q "org.kiwix.desktop"; then
    KIWIX_BIN="flatpak run org.kiwix.desktop"
else
    # Fallback: search for any kiwix AppImage in Apps folder
    KIWIX_BIN=$(find "$HOME/refugiOS/Apps" -name "kiwix-desktop*.appimage" 2>/dev/null | sort | tail -1)
fi

if [ -z "$KIWIX_BIN" ]; then
    echo "$(t error): Kiwix Desktop not found."
    exit 1
fi

# Handle different executable types
if [[ "$KIWIX_BIN" == flatpak* ]]; then
    exec $KIWIX_BIN "$ZIM_FILE"
else
    export APPIMAGE_EXTRACT_AND_RUN=1
    exec "$KIWIX_BIN" "$ZIM_FILE"
fi
