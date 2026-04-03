#!/bin/bash
set -e
FILE="$HOME/refugiOS/Bovedas/datos_personales.img"

if [ -d "$HOME/Escritorio" ]; then DIR="$HOME/Escritorio/MIS_DATOS_SECRETOS"
else DIR="$HOME/Desktop/MIS_DATOS_SECRETOS"; fi

mkdir -p "$DIR"
sudo cryptsetup open "$FILE" boveda_activa
# Transfiere la lectura lógica en `/dev/mapper` a un directorio visible para el interfaz gráfico.
sudo mount /dev/mapper/boveda_activa "$DIR"
sudo chown -R $USER:$USER "$DIR"
echo "La Bóveda está lista para su visualización."
sleep 3
