#!/bin/bash
# ============================================
# refugiOS - Lanzador de Mapas (Organic Maps)
# Detecta modelo RPi y activa software rendering si es necesario
# ============================================

# En Raspberry Pi 1, 2, 3 o Zero no hay soporte de OpenGL ES 3.0,
# así que forzamos renderizado por software para que Organic Maps funcione.
if grep -qE "Raspberry Pi ([1-3]|Zero)" /proc/device-tree/model 2>/dev/null; then
    exec flatpak run --env=LIBGL_ALWAYS_SOFTWARE=1 app.organicmaps.desktop
else
    exec flatpak run app.organicmaps.desktop
fi
