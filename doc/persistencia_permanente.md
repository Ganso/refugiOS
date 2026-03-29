# Cómo activar la Persistencia Permanente

Si has creado tu USB manualmente y tienes que añadir la palabra `persistent` cada vez que arrancas, sigue esta guía para corregirlo de forma definitiva **desde el propio refugiOS**.

## Pasos para el parche definitivo:

### 1. Preparar el entorno
Abre una terminal (`Ctrl+Alt+T`) y crea una carpeta para acceder a los archivos de arranque del USB:
```bash
sudo mkdir -p /mnt/boot_usb
```

### 2. Localizar tu partición de arranque del USB
Para no tocar el disco duro de tu ordenador por error, primero identifica cuál es tu partición de arranque en el USB:
```bash
lsblk -o NAME,FSTYPE,LABEL,SIZE,MOUNTPOINT
```
*   Busca tu unidad USB (normalmente tiene el tamaño de tu pendrive: 32G, 64G, etc.).
*   La partición que buscamos es la pequeña (unos pocos MB) con formato **vfat**. 
*   Anota su nombre (ejemplo: `sdb2`, `sdc2`, etc.).

### 3. Montar la partición
Si la partición tiene la etiqueta **ESP**, el primer comando debería funcionar. Si no, usa el segundo con el nombre que has anotado:
```bash
# Opción A (Si tiene etiqueta ESP):
sudo mount /dev/disk/by-label/ESP /mnt/boot_usb

# Opción B (Manual): Sustituye 'sdX2' por el nombre que anotaste en el paso anterior
# sudo mount /dev/sdX2 /mnt/boot_usb
```

### 4. Aplicar el parche
Estos comandos buscarán automáticamente las líneas del menú de arranque y añadirán `persistent` de forma segura:
```bash
# Añadir 'persistent' antes del separador estándar ' ---'
sudo sed -i '/linux/ s/ ---/ persistent ---/' /mnt/boot_usb/boot/grub/grub.cfg 2>/dev/null
sudo sed -i '/linux/ s/ ---/ persistent ---/' /mnt/boot_usb/EFI/BOOT/grub.cfg 2>/dev/null
```

### 5. Desmontar y Reiniciar
Una vez terminado, desmonta la partición para guardar los cambios:
```bash
sudo umount /mnt/boot_usb
```

¡Ya está! Ahora el sistema arrancará con persistencia automáticamente en cada inicio.
