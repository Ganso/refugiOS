#!/bin/bash
# ============================================
# refugiOS - Maps Launcher (Organic Maps)
# Detects RPi model and activates software rendering if necessary
# ============================================

SCRIPTS_DIR="$HOME/refugiOS/Scripts"

# Source localization system
t() { echo "$1"; }
[ -s "$SCRIPTS_DIR/i18n.sh" ] && source "$SCRIPTS_DIR/i18n.sh"

# In Raspberry Pi 1, 2, 3 or Zero there is no OpenGL ES 3.0 support,
# so we force software rendering for Organic Maps to work.
if grep -qE "Raspberry Pi ([1-3]|Zero)" /proc/device-tree/model 2>/dev/null; then
    exec flatpak run --env=LIBGL_ALWAYS_SOFTWARE=1 app.organicmaps.desktop
else
    exec flatpak run app.organicmaps.desktop
fi
