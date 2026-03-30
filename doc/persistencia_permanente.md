# Persistencia Permanente (Parche para modo `dd`)

Si ya has creado tu USB usando `dd` (o un clonado directo) y no quieres volver a grabarlo, la partición del sistema es de solo lectura. Sin embargo, puedes aprovechar la partición **ESP/EFI** (que sí es escribible) para crear un menú de arranque personalizado que active la persistencia automáticamente.

Sigue estos pasos **desde tu sistema anfitrión (Linux)** antes de arrancar el USB:

### 1. Identificar las particiones
Inserta el USB y abre una terminal:
```bash
lsblk -o NAME,FSTYPE,LABEL,SIZE,MOUNTPOINT
```
*   Busca la partición pequeña del USB con formato **vfat** (suele llamarse `ESP` o tener unos 5-100 MB).
*   Anota su identificador (ejemplo: `/dev/sdb2`).

### 2. Montar la partición de arranque (ESP)
Crea una carpeta temporal y monta la partición:
```bash
sudo mkdir -p /mnt/parche_usb
sudo mount /dev/sdX2 /mnt/parche_usb  # <-- Sustituye sdX2 por la tuya
```

### 3. Crear el nuevo menú de arranque
Vamos a crear un archivo `grub.cfg` que "engañe" al sistema para que arranque con persistencia. Ejecuta este bloque de comandos completo:

```bash
sudo mkdir -p /mnt/parche_usb/EFI/boot

cat <<EOF | sudo tee /mnt/parche_usb/EFI/boot/grub.cfg
set default=0
set timeout=1

menuentry "refugiOS (Persistencia Permanente)" {
    # Busca la partición del sistema por la presencia del kernel
    search --no-floppy --file --set=root /casper/vmlinuz
    
    # Carga el kernel y el disco de inicio con el parámetro 'persistent'
    linux /casper/vmlinuz boot=casper persistent quiet splash ---
    initrd /casper/initrd
}
EOF
```

### 4. Guardar y Desmontar
Asegúrate de que los cambios se escriban en el USB y desmóntalo de forma segura:
```bash
sudo umount /mnt/parche_usb
```

---

¡Listo! Al arrancar de nuevo desde este USB, el equipo encontrará primero tu nuevo archivo configurado y activará la persistencia sin que tengas que tocar nada.
