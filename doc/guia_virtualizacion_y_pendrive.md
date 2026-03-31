# Guía de Preparación de RefugiOS (Modo Live USB Persistente)

Esta guía explica el **único método recomendado** para montar RefugiOS: crear una imagen de disco virtual que se comporte exactamente como un **Live USB con persistencia**. 

Este método es superior porque protege la vida útil de tu hardware, permite réplicas exactas y mantiene el sistema en un estado "inmune" (sólo cambia lo que tú guardes).

> [!IMPORTANT]
> Esta guía asume que estás utilizando **Linux**. El proceso en Windows es propenso a errores y no se recomienda para este nivel de personalización técnica.

---

## 1. Preparación del "contenedor" (La Imagen)

Primero creamos un archivo que simulará ser nuestro pendrive físico.

```bash
# Crea un archivo vacío de 64GB (no ocupa espacio real hasta que lo llenas)
truncate -s 64G refugios.img
```

---

## 2. Volcado de la ISO y Particionado

Utilizaremos dispositivos *loop* para tratar el archivo `.img` como si fuera un disco físico conectado a tu PC.

1.  **Asociar la imagen:**
    ```bash
    sudo losetup -fP refugios.img
    # Identifica el dispositivo (normalmente /dev/loop0)
    losetup -a
    ```
2.  **Volcar la ISO de Xubuntu:**
    ```bash
    # Sustituye /dev/loop0 por el tuyo si es distinto
    sudo dd if=xubuntu-24.04-minimal-amd64.iso of=/dev/loop0 bs=4M status=progress
    ```
3.  **Crear la partición de datos (`writable`):**
    ```bash
    sudo fdisk /dev/loop0
    # Comandos en orden:
    # 'n' -> Nueva partición
    # 'p' -> Primaria
    # '3' -> Muy importante: debe ser la partición 3
    # 'Enter' -> Primer sector por defecto
    # 'Enter' -> Último sector (ocupa todo el resto)
    # 'w' -> Escribir cambios y salir
    ```
4.  **Formatear y etiquetar:**
    ```bash
    # Sincroniza para que el kernel vea la nueva partición
    sudo partprobe /dev/loop0
    # Formatea con la etiqueta mágica que Linux busca para la persistencia
    sudo mkfs.ext4 -L writable /dev/loop0p3
    ```

---

## 3. Estabilización de la Persistencia en el arranque

Por defecto, Xubuntu no sabe que debe usar la partición que acabas de crear. Para que no tengas que pulsar `e` y escribir `persistent` en cada arranque, debes modificar el menú de GRUB dentro de la imagen.

👉 **Guía Externa Recomendada:** [Cómo hacer que el parámetro 'persistent' sea permanente en el GRUB de un Live USB](https://vampii.medium.com/configurar-persistencia-en-ubuntu-live-usb-de-forma-permanente-3e758a5f2e6b)

*Resumen del proceso:* Debes montar la partición EFI de tu imagen (loop0p1), localizar el archivo `grub.cfg` y añadir la palabra `persistent` después de `quiet splash`.

---

## 4. Ejecución y Configuración en VM

Ahora que la imagen está preparada, lánzala en una Máquina Virtual para instalar RefugiOS usando el script oficial.

```bash
# Ejecutar con QEMU (Método más directo)
sudo qemu-system-x86_64 \
  -enable-kvm \
  -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios.img,format=raw
```

Una vez dentro del escritorio de Xubuntu virtual:
1.  Abre una terminal.
2.  Lanza el instalador:
    ```bash
    udo apt install curl -y
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
    ```

---

## 5. Volcado final al Pendrive

Cuando RefugiOS esté configurado a tu gusto dentro de la VM, cierra la máquina y vuelca la imagen final a tu hardware real:

```bash
# ¡ASEGÚRATE de que /dev/sdX es tu USB real con 'lsblk'!
sudo dd if=refugios.img of=/dev/sdX bs=4M status=progress
sync
```

¡Ya tienes un RefugiOS persistente, estable y listo para cualquier emergencia!
