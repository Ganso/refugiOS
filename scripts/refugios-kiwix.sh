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
    if [ -n "$DISPLAY" ] && command -v zenity >/dev/null 2>&1; then
        zenity --error --title="Kiwix" --text="$(t zim_not_found): $ZIM_FILE" --width=400 2>/dev/null || true
    fi
    exit 1
fi

# Recent Kiwix AppImages need glibc 2.35 or newer (Ubuntu 22.04, Debian 12). On
# older systems they die at start with "GLIBC_2.34 not found" (issue #10), so
# there the Flatpak, which carries its own libraries, goes first.
KIWIX_APPIMAGE_MIN_GLIBC="2.35"

glibc_too_old() {
    local version
    version=$(getconf GNU_LIBC_VERSION 2>/dev/null | awk '{print $2}')
    [ -n "$version" ] || return 1
    [ "$(printf '%s\n%s\n' "$KIWIX_APPIMAGE_MIN_GLIBC" "$version" | sort -V | head -1)" != "$KIWIX_APPIMAGE_MIN_GLIBC" ]
}

has_kiwix_flatpak() {
    flatpak list --app 2>/dev/null | grep -q "org.kiwix.desktop"
}

find_kiwix_appimage() {
    if [ -f "$HOME/refugiOS/Apps/kiwix-desktop.appimage" ]; then
        echo "$HOME/refugiOS/Apps/kiwix-desktop.appimage"
        return
    fi
    # Any runnable kiwix AppImage in the Apps folder (newest version)
    find "$HOME/refugiOS/Apps" -name "kiwix-desktop*.appimage" -type f -executable 2>/dev/null | sort -V | tail -1
}

# Detect available Kiwix executable
KIWIX_APPIMAGE=$(find_kiwix_appimage)
if command -v kiwix-desktop &>/dev/null; then
    KIWIX_BIN="kiwix-desktop"
elif glibc_too_old && has_kiwix_flatpak; then
    KIWIX_BIN="flatpak run org.kiwix.desktop"
elif [ -n "$KIWIX_APPIMAGE" ]; then
    KIWIX_BIN="$KIWIX_APPIMAGE"
elif has_kiwix_flatpak; then
    KIWIX_BIN="flatpak run org.kiwix.desktop"
else
    KIWIX_BIN=""
fi

if [ -z "$KIWIX_BIN" ]; then
    echo "$(t error): Kiwix Desktop not found."
    if [ -n "$DISPLAY" ] && command -v zenity >/dev/null 2>&1; then
        zenity --error --title="Kiwix" --text="$(t kiwix_not_found)" --width=400 2>/dev/null || true
    fi
    exit 1
fi

# Handle different executable types
if [[ "$KIWIX_BIN" == flatpak* ]]; then
    # Flatpak sandbox needs explicit filesystem access to the ZIM directory
    ZIM_DIR=$(dirname "$ZIM_FILE")
    exec flatpak run --filesystem="${ZIM_DIR}:ro" org.kiwix.desktop "$ZIM_FILE"
else
    export APPIMAGE_EXTRACT_AND_RUN=1
    exec "$KIWIX_BIN" "$ZIM_FILE"
fi
