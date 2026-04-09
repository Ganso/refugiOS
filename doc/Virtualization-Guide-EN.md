# Guide for Preparing refugiOS in a Virtualized Environment (Live USB Persistent Mode)

This guide explains the **recommended method** to set up refugiOS for users with technical knowledge: Create a virtual disk image that behaves exactly like a **Live USB with persistence**.

This approach protects your pendrive's lifespan, allows you to create identical copies, and keeps the base system immutable (only your data and persistent configuration change).

> [!IMPORTANT]
> This guide is written for **Linux** (preferably Ubuntu or Debian). If you use **Windows**, check the specific notes in the section below.

---

### 💡 Notes for Windows users

If you don't have a Linux computer, you can perform the entire process using only **[VirtualBox](https://www.virtualbox.org/)** (free):

1.  **Install VirtualBox** from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads) and download the **[Xubuntu](https://xubuntu.org/download/)** ISO (the same one you'll use for refugiOS).
2.  **Create a virtual machine** in VirtualBox with these characteristics:
    *   Type: Linux / Ubuntu (64-bit)
    *   Enable **EFI** (*System → Enable EFI*)
    *   RAM: **4 GB** or more
    *   Virtual hard disk: Create a **VMDK type** disk, fixed size of **64 GB** (or the size of your target pendrive). This disk will act as the `refugios.img` file.
    *   Mount the Xubuntu ISO as a virtual CD-ROM.
3.  **Start the VM** and choose *"Try Xubuntu"* (Live mode). You are now in a full Linux system.
4.  **Follow the guide from section 1** exactly as written, using the terminal inside the virtual Live session. The commands `truncate`, `losetup`, `dd`, `fdisk`, `mkfs.ext4`, etc., will work with total normality.
5.  **When you finish**, turn off the VM. The VMDK disk contains your ready image.
6.  **Dump to pendrive:** Convert the VMDK to a raw image and write it to the USB with **[Rufus](https://rufus.ie/)** (in *DD Image* mode) or **[balenaEtcher](https://etcher.balena.io/)**. To convert the disk:
    ```
    VBoxManage clonemedium disk refugios.vmdk refugios.img --format RAW
    ```
    This command is executed from the Windows terminal (cmd or PowerShell) in the directory where VirtualBox saves the VM disks.

> [!WARNING]
> Before dumping the image to the pendrive, open *Disk Management* (`diskmgmt.msc`) in Windows to verify which disk corresponds to your USB. Never write on the wrong disk!

---

## 1. Preparation of the "Container" (the image)

First, we create a file that will simulate being our physical pendrive.

```bash
# Create an empty 60GB file (it doesn't occupy real space until you fill it)
truncate -s 60G refugios.img
```

You can adjust the size (for example 32G, 16G, etc.) according to the real capacity of your pendrive.

Do not adjust the file size to the limit; always leave a few gigabytes of margin, because there are always small differences between the announced size and the real size of the devices. In the example, we have been very conservative for a 64GB pendrive, but depending on the one you are going to use, you can adjust more to the announced size.

---

## 2. ISO Dumping and Partitioning

We will use *loop* devices to treat the `.img` file as if it were a physical disk connected to your PC.

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

    The ISO can be any RefugiOS-compatible Xubuntu/Ubuntu variant; simply adjust the ISO filename.

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

    We use partition 4 (p4) following the typical scheme of many live images (ESP, system, persistent data).

4. **Format and label the persistence partition:**

    ```bash
    # Synchronize so the kernel sees the new partition
    sudo partprobe /dev/loop0

    # Format with the label Ubuntu looks for for modern persistence
    sudo mkfs.ext4 -L writable /dev/loop0p4
    ```

    In recent versions of Ubuntu and derivatives, the persistence partition is usually labeled `writable` instead of the classic `casper-rw`, but the boot mechanism remains the same.

---

## 3. Stabilization of Persistence at Boot (GRUB within the image)

By default, the live system doesn't know it should use the `writable` partition you just created; to activate it, you must boot with the kernel parameter `persistent`.

Official Ubuntu documentation on LiveCD explains that to enable persistence, it's enough to add the word `persistent` to the kernel parameter line at boot:

- **LiveCD/Persistence (Ubuntu Community Help Wiki)** https://help.ubuntu.com/community/LiveCD/Persistence

- **LiveUsbPendrivePersistent (Ubuntu Wiki)** https://wiki.ubuntu.com/LiveUsbPendrivePersistent

These pages detail that by adding `persistent` to the kernel boot line, the system will use the available persistent storage (file or partition with the appropriate label).

In your case, you boot from GRUB (included within the ISO/image itself), so the goal is the same: **the `linux` line of the GRUB that boots Xubuntu should include `persistent` permanently**, without having to edit it manually at each boot.

### 3.1. Official Guide to Modifying Kernel Parameters in GRUB

Ubuntu documents generically how to add and persist kernel parameters in GRUB:

- **How to modify kernel boot parameters – Ubuntu documentation** https://documentation.ubuntu.com/real-time/latest/how-to/modify-kernel-boot-parameters/

Although the context of the document is *Real-time Ubuntu*, the part dedicated to GRUB describes the same mechanism we use here: temporarily editing the `linux` line in the GRUB menu to test parameters and, once the result is verified, making them permanent by modifying the configuration that GRUB uses.

### 3.2. Concrete Steps to Make `persistent` Permanent

1. **Mount the EFI (ESP) Partition of the Image:**

   ```bash
   # Assuming you are still using /dev/loop0
   sudo mkdir -p /mnt/refugios-efi
   sudo mount /dev/loop0p2 /mnt/refugios-efi
   ```

2. **Create a live `grub.cfg`:**

In modern ISOs, GRUB is embedded in the EFI partition, so we have to create a new one:

   ```bash
   sudo mkdir -p /mnt/refugios-efi/boot/grub/
   sudo nano /mnt/refugios-efi/boot/grub/grub.cfg
   ```

Paste this content into the new file:

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

   From this moment on, every time you boot the RefugiOS image, GRUB will pass the `persistent` parameter to the kernel and the system will automatically use the `writable` partition for persistence.

4. **Unmount and Close the Loop:**

   ```bash
   sudo umount /mnt/refugios-efi
   sudo losetup -d /dev/loop0
   ```

---

## 4. Execution and Configuration in VM

Now that the image is prepared, launch it in a Virtual Machine to install and configure RefugiOS using the official script.

```bash
# Run with QEMU (simple method with UEFI)
sudo qemu-system-x86_64   -enable-kvm   -m 4G   -bios /usr/share/ovmf/OVMF.fd   -drive file=refugios.img,format=raw
```

Once inside the virtual Xubuntu desktop:

1. Open a terminal.
2. Launch the official RefugiOS installer:

   ```bash
   sudo apt install curl -y
   curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
   ```

---

## 5. Final Dump to Physical Pendrive

When RefugiOS is configured to your liking within the VM and you've checked that persistence works as expected, close the virtual machine and dump the final image to your real pendrive:

```bash
# MAKE SURE /dev/sdX is your real USB with 'lsblk'!
sudo dd if=refugios.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

- Always verify with `lsblk` or `fdisk -l` which is the real device of your USB before running `dd`.
- After dumping, you can boot from that USB on any compatible machine, with RefugiOS and your persistent data on the `writable` partition.

You now have a persistent, stable RefugiOS ready for any emergency, with persistence managed via GRUB and supported by official Ubuntu documentation!
