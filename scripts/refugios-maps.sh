#!/bin/bash
# ============================================
# refugiOS - Maps Launcher (Organic Maps)
# Detects RPi model and activates software rendering if necessary
# ============================================

SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

# Check if Organic Maps Flatpak is installed
if ! command -v flatpak >/dev/null 2>&1 || ! flatpak list --app 2>/dev/null | grep -q "app.organicmaps.desktop"; then
    ERR_MSG="$(t maps_not_installed)"
    echo -e "\e[1;31m[X] $(t error):\e[0m $ERR_MSG"
    if [ -n "$DISPLAY" ] && command -v zenity >/dev/null 2>&1; then
        zenity --error --title="$(t maps_title)" --text="$ERR_MSG" --width=400 2>/dev/null || true
    else
        read -p "$(t press_enter)" -r || true
    fi
    exit 1
fi

# In Raspberry Pi 1, 2, 3 or Zero there is no OpenGL ES 3.0 support,
# so we force software rendering for Organic Maps to work.
if grep -qE "Raspberry Pi ([1-3]|Zero)" /proc/device-tree/model 2>/dev/null; then
    exec flatpak run --env=LIBGL_ALWAYS_SOFTWARE=1 app.organicmaps.desktop
else
    exec flatpak run app.organicmaps.desktop
fi
