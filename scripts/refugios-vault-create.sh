#!/bin/bash
set -e
FILE="$HOME/refugiOS/Bovedas/datos_personales.img"
echo "Creando contenedor inicial sellado de 3 GB de almacenamiento..."
# dd se encarga de rellenar de datos aleatorios todo el recuadro que luego ocuparemos.
dd if=/dev/urandom of="$FILE" bs=1M count=3072 status=progress
sudo cryptsetup luksFormat "$FILE"
sudo cryptsetup open "$FILE" boveda_activa
sudo mkfs.ext4 /dev/mapper/boveda_activa
sudo cryptsetup close boveda_activa
echo "Bóveda fabricada e injertada. La sesión ya puede cerrarse con seguridad transcurridos 5 segundos..."
sleep 5
