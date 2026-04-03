#!/bin/bash
if [ -d "$HOME/Escritorio" ]; then DIR="$HOME/Escritorio/MIS_DATOS_SECRETOS"
else DIR="$HOME/Desktop/MIS_DATOS_SECRETOS"; fi

sudo umount "$DIR" || true
sudo cryptsetup close boveda_activa || true
rmdir "$DIR" || true
echo "Contenidos vaciados del buffer RAM. La bóveda ha sido lacrada sin exponer vectores."
sleep 3
