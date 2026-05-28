# Virtualization Guide: Testing refugiOS Before Flashing

This guide explains how to test any refugiOS image in a virtual machine before flashing it to a physical USB drive. It is the fastest way to verify that everything works correctly without needing to restart your computer.

> [!IMPORTANT]
> This guide applies to **x86 systems (PC and Xubuntu)**. Raspberry Pi uses ARM architecture and requires real hardware to test.

---

## What Can You Test in a Virtual Machine?

| Image | Source | Difficulty |
| :--- | :--- | :--- |
| **Pre-built image** | [Direct download](https://refugios.ganso.org/) | Easy — just download and boot |
| **Self-built image** | `scripts/build_refugios.sh` | Medium — requires building first |
| **Xubuntu Live USB** | Xubuntu ISO + persistence | Advanced — requires GRUB configuration |

---

## 1. Testing the Pre-built Image (Fastest Method)

If you have downloaded the pre-built refugiOS image, you can test it directly in a virtual machine:

### With QEMU (Linux)

```bash
sudo qemu-system-x86_64 -enable-kvm -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios-base-16G-en.img,format=raw
```

If KVM is not available, remove `-enable-kvm` (booting will be much slower).

To install the required dependencies:

| Distribution | Command |
| :--- | :--- |
| **Debian / Ubuntu** | `sudo apt install ovmf qemu-system-x86` |
| **Fedora** | `sudo dnf install edk2-ovmf qemu-system-x86-core` |
| **Arch Linux** | `sudo pacman -S edk2-ovmf qemu-system-x86` |

### With VirtualBox (Windows, macOS, Linux)

1. Create a new virtual machine: type **Linux / Ubuntu (64-bit)**.
2. Enable **EFI** (*System → Enable EFI*).
3. Assign **4 GB of RAM** or more.
4. In **Storage**, attach the `.img` file as a virtual hard disk:
   - If necessary, convert it to VDI first: `VBoxManage convertdd refugios-base-16G-en.img refugios.vdi`
5. Start the virtual machine.

### With the test script (if you built the image)

If you generated the image with `build_refugios.sh`, you can use the automated test script:

```bash
bash scripts/test_boot.sh 16G
```

This script automatically detects UEFI firmware and KVM acceleration. See the **[System Image Build Guide](System-Image-Build-EN.md)** for more details.

### What to Expect on Boot

When booting you will see:

1. The **GRUB** bootloader with the refugiOS entry.
2. **LightDM** automatically logging in as the `refugios` user.
3. The **XFCE** desktop with:
   - The **"Complete refugiOS installation"** launcher on the desktop.
   - The welcome popup showing the disk size and recommended steps.

To complete the installation, connect to the network (already enabled by default in QEMU and VirtualBox) and double-click the desktop launcher, or run in the terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

---

## 2. Testing a Self-built Image

If you have generated an image with `scripts/build_refugios.sh`, the process is the same as the previous section, just change the filename:

```bash
sudo qemu-system-x86_64 -enable-kvm -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios-base-16G.img,format=raw
```

Or use the automated script:

```bash
bash scripts/test_boot.sh
```

> [!NOTE]
> For full details on the image building process, see the **[System Image Build Guide](System-Image-Build-EN.md)**.

---

## 3. Testing the Xubuntu Live USB Method (Advanced)

If you want to test the alternative approach based on Xubuntu with persistence, follow these steps. This method requires more configuration but allows you to work with a complete Live image in the VM before flashing it to a physical USB.

> [!IMPORTANT]
> This section is written for **Linux** (preferably Ubuntu or Debian). If you use **Windows**, see the specific notes at the end of this section.

### 3.1. Preparing the Container (the image)

First, we create a file that will simulate being our physical USB drive:

```bash
# Create an empty 60GB file (it doesn't occupy real space until you fill it)
truncate -s 60G refugios.img
```

You can adjust the size (for example 32G, 16G, etc.) according to the real capacity of your USB drive. Do not adjust to the limit: always leave a few gigabytes of margin.

### 3.2. ISO Dumping and Partitioning

We will use *loop* devices to treat the `.img` file as if it were a physical disk:

1. **Associate the image as a loop:**

```bash
sudo losetup -fP refugios.img
# Identify the device (usually /dev/loop0)
sudo losetup -a
```

2. **Dump the Xubuntu ISO into the loop:**

```bash
# Replace /dev/loop0 with the one assigned by losetup
sudo dd if=xubuntu-24.04-minimal-amd64.iso of=/dev/loop0 bs=4M status=progress conv=fsync
```

3. **Create the data partition (`writable`):**

```bash
sudo fdisk /dev/loop0
# Commands in order:
# 'n' -> New partition
# 'Enter' -> Normally it will be the fourth partition
# 'Enter' -> Default first sector
# 'Enter' -> Last sector (occupies all the rest)
# 'w' -> Write changes and exit
```

4. **Format and label the persistence partition:**

```bash
sudo partprobe /dev/loop0
sudo mkfs.ext4 -L writable /dev/loop0p4
```

### 3.3. Enabling Persistence in GRUB

By default, the live system does not use the `writable` partition. You need to add the `persistent` parameter to the kernel line in GRUB.

1. **Mount the EFI (ESP) partition of the image:**

```bash
sudo mkdir -p /mnt/refugios-efi
sudo mount /dev/loop0p2 /mnt/refugios-efi
```

2. **Create a live `grub.cfg`:**

```bash
sudo mkdir -p /mnt/refugios-efi/boot/grub/
sudo nano /mnt/refugios-efi/boot/grub/grub.cfg
```

Paste this content:

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

3. **Unmount and close the loop:**

```bash
sudo umount /mnt/refugios-efi
sudo losetup -d /dev/loop0
```

### 3.4. Booting in the Virtual Machine

With QEMU:

```bash
sudo qemu-system-x86_64 -enable-kvm -m 4G \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=refugios.img,format=raw
```

Inside the virtual Xubuntu desktop, run the installer:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

### 3.5. Final Dump to the Physical USB

When refugiOS is configured to your liking within the VM, dump the image to the real USB:

```bash
# MAKE SURE /dev/sdX is your real USB with 'lsblk'!
sudo dd if=refugios.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

> [!WARNING]
> Always verify with `lsblk` or `fdisk -l` which is the real USB device before running `dd`. Writing to the wrong disk will destroy all data on that disk!

---

## 4. Notes for Windows Users

If you don't have a Linux computer, you can perform the entire process in section 3 (Xubuntu Live USB) using only **[VirtualBox](https://www.virtualbox.org/)** (free):

1. **Install VirtualBox** from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads) and download the **[Xubuntu](https://xubuntu.org/download/)** ISO.
2. **Create a virtual machine** in VirtualBox with these characteristics:
   - Type: Linux / Ubuntu (64-bit)
   - Enable **EFI** (*System → Enable EFI*)
   - RAM: **4 GB** or more
   - Virtual hard disk: Create a **VMDK type** disk, fixed size of **64 GB** (or the size of your target USB drive)
   - Mount the Xubuntu ISO as a virtual CD-ROM.
3. **Start the VM** and choose *"Try Xubuntu"* (Live mode). You are now in a full Linux system.
4. **Follow section 3** exactly as written, using the terminal inside the virtual Live session.
5. **When you finish**, turn off the VM. The VMDK disk contains your ready image.
6. **Dump to USB:** Convert the VMDK to a raw image and write it to the USB with **[Rufus](https://rufus.ie/)** (in *DD Image* mode) or **[balenaEtcher](https://etcher.balena.io/)**:
   ```
   VBoxManage clonemedium disk refugios.vmdk refugios.img --format RAW
   ```

For the pre-built image, you can use Rufus or balenaEtcher directly to flash the downloaded `.img` file to your USB, without needing a virtual machine.

> [!WARNING]
> Before flashing the image to the USB drive, open *Disk Management* (`diskmgmt.msc`) in Windows to verify which disk corresponds to your USB. Never write on the wrong disk!

---

[📖 Back to documentation](../README.en.md)