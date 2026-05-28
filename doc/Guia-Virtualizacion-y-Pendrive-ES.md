# Guía de Virtualización: Probar refugiOS antes de grabarlo

Esta guía explica cómo probar cualquier imagen de refugiOS en una máquina virtual antes de grabarla en un USB físico. Es el método más rápido para comprobar que todo funciona correctamente sin necesidad de reiniciar tu ordenador.

> [!IMPORTANT]
> Esta guía aplica a **sistemas x86 (PC y Xubuntu)**. La Raspberry Pi usa arquitectura ARM y requiere hardware real para probarse.

---

## ¿Qué puedes probar en una máquina virtual?

| Imagen | Origen | Dificultad |
| :--- | :--- | :--- |
| **Imagen pregenerada** | [Descarga directa](https://refugios.ganso.org/) | Fácil — solo descargar y arrancar |
| **Imagen construida por ti** | `scripts/build_refugios.sh` | Media — requerirá generarla primero |
| **Live-USB de Xubuntu** | ISO de Xubuntu + persistencia | Avanzada — requiere configurar GRUB |

---

## 1. Probar la imagen pregenerada (el método más rápido)

Si has descargado la imagen pregenerada de refugiOS, puedes probarla directamente en una máquina virtual:

### Con QEMU (Linux)

```bash
sudo qemu-system-x86_64 -enable-kvm -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios-base-16G-es.img,format=raw
```

Si no tienes KVM disponible, elimina `-enable-kvm` (el arranque será mucho más lento).

Para instalar las dependencias necesarias:

| Distribución | Comando |
| :--- | :--- |
| **Debian / Ubuntu** | `sudo apt install ovmf qemu-system-x86` |
| **Fedora** | `sudo dnf install edk2-ovmf qemu-system-x86-core` |
| **Arch Linux** | `sudo pacman -S edk2-ovmf qemu-system-x86` |

### Con VirtualBox (Windows, macOS, Linux)

1. Crea una nueva máquina virtual: tipo **Linux / Ubuntu (64-bit)**.
2. Habilita **EFI** (*Sistema → Habilitar EFI*).
3. Asigna **4 GB de RAM** o más.
4. En **Almacenamiento**, adjunta el archivo `.img` como disco duro virtual:
   - Si es necesario, conviértelo primero a VDI: `VBoxManage convertdd refugios-base-16G-es.img refugios.vdi`
5. Arranca la máquina virtual.

### Con el script de prueba (si construiste la imagen)

Si generaste la imagen con `build_refugios.sh`, puedes usar el script automatizado de prueba:

```bash
bash scripts/test_boot.sh 16G
```

Este script detecta automáticamente el firmware UEFI y la aceleración KVM. Consulta la **[Guía de Construcción de Imagen de Sistema](Construccion-Imagen-Sistema-ES.md)** para más detalles.

### Qué esperar al arrancar

Al arrancar verás:

1. El cargador **GRUB** con la entrada de refugiOS.
2. **LightDM** iniciando sesión automáticamente como el usuario `refugios`.
3. El escritorio **XFCE** con:
   - El lanzador **"Completar instalación de refugiOS"** en el escritorio.
   - El popup de bienvenida mostrando el tamaño del disco y los pasos recomendados.

Para completar la instalación, conéctate a la red (ya habilitada por defecto en QEMU y VirtualBox) y haz doble clic en el lanzador del escritorio, o ejecuta en la terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

---

## 2. Probar una imagen construida por ti

Si has generado una imagen con `scripts/build_refugios.sh`, el proceso es el mismo que en la sección anterior, solo cambia el nombre del archivo:

```bash
sudo qemu-system-x86_64 -enable-kvm -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios-base-16G.img,format=raw
```

O usa el script automatizado:

```bash
bash scripts/test_boot.sh
```

> [!NOTE]
> Para los detalles completos del proceso de construcción de la imagen, consulta la **[Guía de Construcción de Imagen de Sistema](Construccion-Imagen-Sistema-ES.md)**.

---

## 3. Probar el método Live-USB de Xubuntu (avanzado)

Si quieres probar el enfoque alternativo basado en Xubuntu con persistencia, sigue estos pasos. Este método requiere más configuración pero te permite trabajar con una imagen Live completa en la VM antes de volcarla a un USB físico.

> [!IMPORTANT]
> Esta sección está escrita para **Linux** (preferiblemente Ubuntu o Debian). Si usas **Windows**, consulta las notas específicas al final de esta sección.

### 3.1. Preparación del contenedor (la imagen)

Primero creamos un archivo que simulará ser nuestro pendrive físico:

```bash
# Crea un archivo vacío de 60G (no ocupa espacio real hasta que lo llenas)
truncate -s 60G refugios.img
```

Puedes ajustar el tamaño (por ejemplo 32G, 16G, etc.) según la capacidad real de tu pendrive. No ajustes al límite: deja siempre unos gigas de margen.

### 3.2. Volcado de la ISO y particionado

Utilizaremos dispositivos *loop* para tratar el archivo `.img` como si fuera un disco físico:

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

4. **Formatear y etiquetar la partición de persistencia:**

```bash
sudo partprobe /dev/loop0
sudo mkfs.ext4 -L writable /dev/loop0p4
```

### 3.3. Habilitar la persistencia en GRUB

Por defecto, el sistema live no usa la partición `writable`. Hay que añadir el parámetro `persistent` a la línea del kernel en GRUB.

1. **Montar la partición EFI (ESP) de la imagen:**

```bash
sudo mkdir -p /mnt/refugios-efi
sudo mount /dev/loop0p2 /mnt/refugios-efi
```

2. **Crear un `grub.cfg` del live:**

```bash
sudo mkdir -p /mnt/refugios-efi/boot/grub/
sudo nano /mnt/refugios-efi/boot/grub/grub.cfg
```

Pegar este contenido:

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

3. **Desmontar y cerrar el loop:**

```bash
sudo umount /mnt/refugios-efi
sudo losetup -d /dev/loop0
```

### 3.4. Arrancar en la máquina virtual

Con QEMU:

```bash
sudo qemu-system-x86_64 -enable-kvm -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios.img,format=raw
```

Dentro del escritorio de Xubuntu virtual, ejecuta el instalador:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

### 3.5. Volcado final al USB físico

Cuando refugiOS esté configurado a tu gusto dentro de la VM, vuelca la imagen al USB real:

```bash
# ¡ASEGÚRATE de que /dev/sdX es tu USB real con 'lsblk'!
sudo dd if=refugios.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

> [!WARNING]
> Verifica siempre con `lsblk` o `fdisk -l` cuál es el dispositivo real de tu USB antes de ejecutar `dd`. ¡Escribir en el disco equivocado destruirá todos los datos!

---

## 4. Notas para usuarios de Windows

Si no dispones de un equipo con Linux, puedes realizar todo el proceso de la sección 3 (Live-USB de Xubuntu) utilizando únicamente **[VirtualBox](https://www.virtualbox.org/)** (gratuito):

1. **Instala VirtualBox** desde [virtualbox.org](https://www.virtualbox.org/wiki/Downloads) y descarga la ISO de **[Xubuntu](https://xubuntu.org/download/)**.
2. **Crea una máquina virtual** en VirtualBox con estas características:
   - Tipo: Linux / Ubuntu (64-bit)
   - Habilitar **EFI** (*System → Enable EFI*)
   - RAM: **4 GB** o más
   - Disco duro virtual: Crea un disco de **tipo VMDK**, tamaño fijo de **64 GB** (o el tamaño de tu pendrive destino)
   - Monta la ISO de Xubuntu como CD-ROM virtual.
3. **Arranca la VM** y elige *"Probar Xubuntu"* (modo Live). Ya estás en un Linux completo.
4. **Sigue la sección 3** exactamente como está escrita, usando la terminal dentro de la sesión Live virtual.
5. **Cuando termines**, apaga la VM. El disco VMDK contiene tu imagen lista.
6. **Volcado al pendrive:** Convierte el VMDK a imagen raw y escríbela al USB con **[Rufus](https://rufus.ie/)** (en modo *DD Image*) o **[balenaEtcher](https://etcher.balena.io/)**:
   ```
   VBoxManage clonemedium disk refugios.vmdk refugios.img --format RAW
   ```

Para la imagen pregenerada, puedes usar directamente Rufus o balenaEtcher para grabar el archivo `.img` descargado en tu USB, sin necesidad de máquina virtual.

> [!WARNING]
> Antes de volcar la imagen al pendrive, abre *Administración de discos* (`diskmgmt.msc`) en Windows para verificar qué disco corresponde a tu USB. ¡Nunca escribas sobre el disco equivocado!

---

[📖 Volver a la documentación](../README.md)