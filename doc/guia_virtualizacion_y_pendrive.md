# Guía de Preparación de RefugiOS en un entorno virtualizado (Modo Live USB Persistente)

Esta guía explica el **método recomendado** para montar RefugiOS para usuarios con conocimientos técnicos: Crear una imagen de disco virtual que se comporte exactamente como un **Live USB con persistencia**.

Este enfoque protege la vida útil de tu pendrive, permite crear copias idénticas y mantiene el sistema base inmutable (solo cambian tus datos y configuración persistente).

> [!IMPORTANT]
> Esta guía está escrita para **Linux** (preferiblemente Ubuntu o Debian). Si usas **Windows**, consulta las notas específicas en la sección de más abajo.

---

### 💡 Notas para usuarios de Windows

Si no dispones de un equipo con Linux, puedes realizar todo el proceso utilizando únicamente **[VirtualBox](https://www.virtualbox.org/)** (gratuito):

1.  **Instala VirtualBox** desde [virtualbox.org](https://www.virtualbox.org/wiki/Downloads) y descarga la ISO de **[Xubuntu](https://xubuntu.org/download/)** (la misma que usarás para refugiOS).
2.  **Crea una máquina virtual** en VirtualBox con estas características:
    *   Tipo: Linux / Ubuntu (64-bit)
    *   Habilitar **EFI** (*System → Enable EFI*)
    *   RAM: **4 GB** o más
    *   Disco duro virtual: Crea un disco de **tipo VMDK**, tamaño fijo de **64 GB** (o el tamaño de tu pendrive destino). Este disco hará las veces del archivo `refugios.img`.
    *   Monta la ISO de Xubuntu como CD-ROM virtual.
3.  **Arranca la VM** y elige *"Probar Xubuntu"* (modo Live). Ya estás en un Linux completo.
4.  **Sigue la guía desde la sección 1** exactamente como está escrita, usando la terminal dentro de la sesión Live virtual. Los comandos `truncate`, `losetup`, `dd`, `fdisk`, `mkfs.ext4`, etc. funcionarán con total normalidad.
5.  **Cuando termines**, apaga la VM. El disco VMDK contiene tu imagen lista.
6.  **Volcado al pendrive:** Convierte el VMDK a imagen raw y escríbela al USB con **[Rufus](https://rufus.ie/)** (en modo *DD Image*) o **[balenaEtcher](https://etcher.balena.io/)**. Para convertir el disco:
    ```
    VBoxManage clonemedium disk refugios.vmdk refugios.img --format RAW
    ```
    Este comando se ejecuta desde la terminal de Windows (cmd o PowerShell) en el directorio donde VirtualBox guarda los discos de la VM.

> [!WARNING]
> Antes de volcar la imagen al pendrive, abre *Administración de discos* (`diskmgmt.msc`) en Windows para verificar qué disco corresponde a tu USB. ¡Nunca escribas sobre el disco equivocado!

---

## 1. Preparación del "contenedor" (la imagen)

Primero creamos un archivo que simulará ser nuestro pendrive físico.

```bash
# Crea un archivo vacío de 64GB (no ocupa espacio real hasta que lo llenas)
truncate -s 64G refugios.img
```

Puedes ajustar el tamaño (por ejemplo 32G, 16G, etc.) según la capacidad real de tu pendrive.

---

## 2. Volcado de la ISO y particionado

Utilizaremos dispositivos *loop* para tratar el archivo `.img` como si fuera un disco físico conectado a tu PC.

1. **Asociar la imagen como loop:**

    ```bash
    sudo losetup -fP refugios.img
    # Identifica el dispositivo (normalmente /dev/loop0)
    sudo losetup -a
    ```

2. **Volcar la ISO de Xubuntu en el loop:**

    ```bash
    # Sustituye /dev/loop0 por el que te haya asignado losetup
    sudo dd if=xubuntu-24.04-minimal-amd64.iso of=/dev/loop0 bs=4M status=progress conv=fsync
    ```

    La ISO puede ser cualquier variante de Xubuntu/Ubuntu compatible con RefugiOS; simplemente ajusta el nombre del archivo ISO.

3. **Crear la partición de datos (`writable`):**

    ```bash
    sudo fdisk /dev/loop0
    # Comandos en orden:
    # 'n' -> Nueva partición
    # 'Enter' -> Normalmente será la cuarta partición
    # 'Enter' -> Primer sector por defecto
    # 'Enter' -> Último sector (ocupa todo el resto)
    # 'w' -> Escribir cambios y salir
    ```

    Usamos la partición 3 para seguir el esquema típico de muchas imágenes live (ESP, sistema, datos persistentes).

4. **Formatear y etiquetar la partición de persistencia:**

    ```bash
    # Sincroniza para que el kernel vea la nueva partición
    sudo partprobe /dev/loop0

    # Formatea con la etiqueta que busca Ubuntu para la persistencia moderna
    sudo mkfs.ext4 -L writable /dev/loop0p4
    ```

    En versiones recientes de Ubuntu y derivados, la partición de persistencia suele etiquetarse como `writable`, en lugar del clásico `casper-rw`, pero el mecanismo de arranque sigue siendo el mismo.

---

## 3. Estabilización de la persistencia en el arranque (GRUB dentro de la imagen)

Por defecto, el sistema live no sabe que debe usar la partición `writable` que acabas de crear; para activarla hay que arrancar con el parámetro de kernel `persistent`.

La documentación oficial de Ubuntu sobre LiveCD explica que para habilitar la persistencia basta con añadir la palabra `persistent` a la línea de parámetros que se pasa al kernel al arrancar:

- **LiveCD/Persistence (Ubuntu Community Help Wiki)**    https://help.ubuntu.com/community/LiveCD/Persistence

- **LiveUsbPendrivePersistent (Ubuntu Wiki)**    https://wiki.ubuntu.com/LiveUsbPendrivePersistent

En estas páginas se detalla que, al añadir `persistent` a la línea de arranque del kernel, el sistema utilizará el almacenamiento persistente disponible (archivo o partición con la etiqueta adecuada).

En tu caso, arrancas desde GRUB (incluido dentro de la propia ISO/imagen), así que el objetivo es el mismo: **que la línea `linux` del GRUB que arranca Xubuntu incluya `persistent` de forma permanente**, sin tener que editarla a mano en cada arranque.

### 3.1. Guía oficial para modificar parámetros del kernel en GRUB

Ubuntu documenta de forma genérica cómo añadir y persistir parámetros de kernel en GRUB:

- **How to modify kernel boot parameters – Ubuntu documentation**    https://documentation.ubuntu.com/real-time/latest/how-to/modify-kernel-boot-parameters/

Aunque el contexto del documento es *Real-time Ubuntu*, la parte dedicada a GRUB describe el mismo mecanismo que utilizamos aquí: editar temporalmente la línea `linux` en el menú de GRUB para probar parámetros y, una vez verificado el resultado, hacerlos permanentes modificando la configuración que utiliza GRUB.

### 3.2. Pasos concretos para que `persistent` sea permanente

1. **Montar la partición EFI (ESP) de la imagen:**

   ```bash
   # Asumiendo que sigues usando /dev/loop0
   sudo mkdir -p /mnt/refugios-efi
   sudo mount /dev/loop0p2 /mnt/refugios-efi
   ```

2. **Crer un `grub.cfg` del live:**

En las ISO modernas, GRUB está embebido en la partición EFI, así que tenemos que crear uno nuevo:

   ```bash
   sudo nano /mnt/refugios-efi/boot/grub/grub.cfg
   ```

Pegamos este contenido en el nuevo fichero:

   ```
   set timeout=5
   set default=0

   menuentry "Xubuntu RefugiOS (persistent)" {
    set root=(hd0,gpt1)
    linux /casper/vmlinuz boot=casper persistent quiet splash ---
    initrd /casper/initrd
   }

   menuentry "Xubuntu Live (no persistent)" {
    set root=(hd0,gpt1)
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
   }
   ```

   A partir de este momento, cada vez que arranques la imagen RefugiOS, GRUB pasará el parámetro `persistent` al kernel y el sistema utilizará automáticamente la partición `writable` para la persistencia.

4. **Desmontar y cerrar el loop:**

   ```bash
   sudo umount /mnt/refugios-efi
   sudo losetup -d /dev/loop0
   ```

---

## 4. Ejecución y configuración en VM

Ahora que la imagen está preparada, lánzala en una Máquina Virtual para instalar y configurar RefugiOS usando el script oficial.

```bash
# Ejecutar con QEMU (método sencillo con UEFI)
sudo qemu-system-x86_64   -enable-kvm   -m 4G   -bios /usr/share/ovmf/OVMF.fd   -drive file=refugios.img,format=raw
```

Una vez dentro del escritorio de Xubuntu virtual:

1. Abre una terminal.
2. Lanza el instalador oficial de RefugiOS:

   ```bash
   sudo apt install curl -y
   curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
   ```

---

## 5. Volcado final al pendrive físico

Cuando RefugiOS esté configurado a tu gusto dentro de la VM y hayas comprobado que la persistencia funciona como esperas, cierra la máquina virtual y vuelca la imagen final a tu pendrive real:

```bash
# ¡ASEGÚRATE de que /dev/sdX es tu USB real con 'lsblk'!
sudo dd if=refugios.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

- Verifica siempre con `lsblk` o `fdisk -l` cuál es el dispositivo real de tu USB antes de ejecutar `dd`.
- Tras el volcado, podrás arrancar desde ese USB en cualquier máquina compatible, con RefugiOS y tus datos persistentes en la partición `writable`.

¡Ya tienes un RefugiOS persistente, estable y listo para cualquier emergencia, con la persistencia gestionada mediante GRUB y apoyada en documentación oficial de Ubuntu!
