# refugiOS System Image Build Guide

This guide details the automated process for generating a **base refugiOS disk image** from scratch, without depending on a pre-existing Xubuntu ISO. The resulting system is a native Debian Trixie installation with the XFCE desktop, ready to be flashed directly to a USB drive or external device.

Unlike the traditional method based on a Xubuntu Live ISO with persistence, this image produces a **natively installed system**, which eliminates the indirection layers of Live mode and offers better performance, less device wear, and greater control over the base configuration.

> [!IMPORTANT]
> This method is intended for **advanced users** who want to build the image from its source or prepare multiple identical units efficiently. If you just want to get refugiOS running quickly, check the **[XUbuntu Installation Guide](Xubuntu-Installation-EN.md)**.

> [!NOTE]
> The choice of physical device where you will flash the image (SSD, pendrive, SATA adapter) affects the performance and lifespan of your refugiOS. Check the **[Choosing Installation Media Guide](Choosing-Installation-Media-EN.md)** before starting.

---

## 1. Prerequisites

### 1.1. Host Operating System

The build script requires a **Debian-based** operating system (Debian, Ubuntu, Linux Mint, Pop!_OS). If your distribution is not Debian-based, the script will display an error and stop.

The system must be **x86_64 (amd64) architecture**.

### 1.2. Root Permissions

The script must be run as **root** (using `sudo`), as it needs to:
- Create and partition disk images
- Mount filesystems
- Run `debootstrap`
- Configure loop devices
- Install GRUB into the image

### 1.3. Dependencies

The script automatically installs the necessary dependencies if they are not present:
- `debootstrap` — To create the Debian base system from scratch
- `parted` — To partition the image (GPT)
- `dosfstools` — To format the EFI partition (FAT32)
- `e2fsprogs` — To format the root partition (ext4)

For the test script (`test_boot.sh`), you will also need:
- `qemu-system-x86` — QEMU emulator to test booting
- `ovmf` — UEFI firmware for QEMU

Installing test dependencies:

| Distribution | Installation Command |
| :--- | :--- |
| **Debian / Ubuntu** | `sudo apt install ovmf qemu-system-x86` |
| **Fedora** | `sudo dnf install edk2-ovmf qemu-system-x86-core` |
| **Arch Linux** | `sudo pacman -S edk2-ovmf qemu-system-x86` |

> [!NOTE]
> The `build_refugios.sh` script is only compatible with Debian-based systems. However, `test_boot.sh` is compatible with a wider range of distributions (Debian, Ubuntu, Mint, Pop!_OS, Fedora, Arch, Manjaro, openSUSE), as it only needs QEMU and OVMF.

### 1.4. Disk Space

The generated image is a **sparse file**: it is created at the requested size but only occupies the actual space of the written data. A freshly created 16G image will occupy approximately **7-8 GB** on disk. Make sure you have at least **10 GB free** before starting.

---

## 2. Building the Base Image

### 2.1. Running the Script

```bash
sudo bash scripts/build_refugios.sh [SIZE]
```

The `SIZE` parameter is optional and defines the virtual size of the image. The default is **16G**. The format must be a number followed by `G` (gigabytes), `M` (megabytes), or `K` (kilobytes).

Examples:

| Command | Image Size | Generated File Name |
| :--- | :--- | :--- |
| `sudo bash scripts/build_refugios.sh` | 16 GB (default) | `refugios-base-16G.img` |
| `sudo bash scripts/build_refugios.sh 32G` | 32 GB | `refugios-base-32G.img` |
| `sudo bash scripts/build_refugios.sh 64G` | 64 GB | `refugios-base-64G.img` |
| `sudo bash scripts/build_refugios.sh 500M` | 500 MB | `refugios-base-500M.img` |

> [!WARNING]
> The image size should match (or be slightly smaller than) the actual size of the USB device where you will flash it. Manufacturers often advertise capacities slightly larger than the real ones. It is recommended to leave a safety margin.

### 2.2. Internal Script Process

The script automatically executes the following steps:

1. **Environment validation:** Checks that the host is Debian-based, that it runs as root, and that the size is valid.
2. **Dependency installation:** Runs `apt-get update` and installs `debootstrap`, `parted`, `dosfstools`, and `e2fsprogs` if missing.
3. **Sparse image creation:** Uses `truncate -s` to create the `.img` file at the specified size.
4. **GPT partitioning:** Creates two partitions:
   - **Partition 1 (EFI):** FAT32, from 1 MiB to 513 MiB, marked as ESP (EFI System Partition).
   - **Partition 2 (ROOT):** ext4, from 513 MiB to the end of the disk.
5. **Loop device mapping:** Associates the image to a loop device with `losetup -Pf` to access the partitions.
6. **Formatting:** Formats EFI as FAT32 and ROOT as ext4. Obtains the UUIDs of both partitions.
7. **Mounting:** Mounts the root partition at `/mnt/refugios_build` and the EFI partition at `/mnt/refugios_build/boot/efi`.
8. **Debootstrap:** Installs the Debian Trixie (amd64) base system from official repositories.
9. **fstab generation:** Creates `/etc/fstab` with the real UUIDs of both partitions to ensure correct mounting at boot.
10. **Configuration inside chroot:** Mounts `/dev`, `/dev/pts`, `/proc`, `/sys`, and `/run` inside the image and executes all configuration steps in a chroot environment (see section 2.3).
11. **Unmounting and cleanup:** Unmounts everything in reverse order and removes the loop device.

### 2.3. Configuration Inside the Chroot

Inside the chroot environment, the script performs the following configuration:

#### Base System
- Configures Debian Trixie APT repositories (main, contrib, non-free, non-free-firmware) including security and updates.
- Installs essential packages:
  - **Kernel:** `linux-image-amd64`
  - **Bootloader:** `grub-efi-amd64`
  - **System:** `sudo`, `network-manager`
  - **Desktop:** `xfce4`, `xfce4-terminal`, `lightdm`
  - **Tools:** `curl`, `cloud-guest-utils`, `zenity`
  - **Browser:** `epiphany-browser`
- Installs GRUB in **removable** mode (`--removable --no-nvram`), which is vital for the system to boot from a USB drive without needing to register the entry in the host's NVRAM.
- Disables `os-prober` in GRUB to avoid unnecessary warnings.
- Generates GRUB configuration with `update-grub`.

#### Default User
- Creates the `refugios` user with the password `refugios`.
- Adds the user to the `sudo` group.
- Configures **passwordless sudo** for the `refugios` user (`/etc/sudoers.d/refugios`).
- Configures **autologin** in LightDM so the desktop loads automatically without asking for credentials.

#### Network and Hostname
- Hostname: `refugios`
- Configures `/etc/hosts` with standard entries for localhost and IPv6.

#### Disk Auto-Expansion
- Injects the script `/usr/local/bin/refugios-expand.sh` which:
  - Automatically detects the root disk and partition (compatible with NVMe, eMMC, SATA, and loop).
  - Expands the partition with `growpart`.
  - Resizes the filesystem with `resize2fs`.
  - **Automatically disables itself** after successful execution.
- Creates the systemd service `refugios-expand.service` that runs the expansion on the first boot.

#### Desktop Installer Launcher
- Injects `/usr/local/bin/refugios-install-wrapper.sh`, a wrapper that:
  - Checks Internet connectivity by pinging `github.com`.
  - If connected, downloads and runs the official refugiOS installer.
  - If not connected, shows a graphical dialog (zenity) or a terminal message indicating that Internet is needed.
- Creates the desktop launcher `/etc/skel/Desktop/Instalar_refugiOS.desktop` that runs the wrapper from `xfce4-terminal`.
- Copies the launcher to the `refugios` user's desktop.

#### XFCE Desktop Customization
- Hides default desktop icons (Home, Trash, Filesystem, Removable devices) via XFCE XML configuration.

#### First Boot Welcome
- Injects `/usr/local/bin/refugios-welcome.sh`, a script that:
  - Detects the actual boot disk size.
  - Shows a zenity welcome dialog with disk information and recommended steps (adjust resolution, launch installer).
  - **Auto-deletes** after running once (marks `$HOME/.refugios-welcome-done`).

---

## 3. Boot Testing with QEMU

Once the image is generated, you can verify that it boots correctly using the test script before flashing it to a physical device.

### 3.1. Running the Test Script

```bash
bash scripts/test_boot.sh [SIZE]
```

The `SIZE` parameter is optional. If not specified, the script automatically searches for any `refugios-base-*.img` image in the project's root directory.

Examples:

| Command | Behavior |
| :--- | :--- |
| `bash scripts/test_boot.sh` | Finds and uses the first `refugios-base-*.img` image it finds |
| `bash scripts/test_boot.sh 16G` | Uses the `refugios-base-16G.img` image |

> [!NOTE]
> Unlike the build script, `test_boot.sh` **does not require root permissions** (unless `/dev/kvm` needs special permissions for KVM acceleration).

### 3.2. Internal Test Script Process

1. **OVMF firmware detection:** Automatically searches for UEFI firmware files (OVMF) in the standard paths for each distribution:
   - Debian/Ubuntu: `/usr/share/OVMF/`
   - Fedora: `/usr/share/edk2/ovmf/`
   - Arch Linux: `/usr/share/edk2/x64/`
2. **UEFI variables copy:** If separate OVMF code and variables files are found, creates a local writable copy (`refugios_vars.fd`) so QEMU can modify the UEFI boot variables.
3. **KVM detection:** Checks if KVM acceleration is available (`/dev/kvm`). If available, enables it for fast booting; if not, warns that booting will be extremely slow.
4. **QEMU launch:** Runs QEMU with the following parameters:
   - **RAM:** 2 GB
   - **CPUs:** 2
   - **Disk:** The generated raw image
   - **VGA:** virtio
   - **Network:** Network emulation with NAT (nic/user)
   - **UEFI firmware:** Automatically detected (pflash or bios depending on the available format)

### 3.3. Inside the Virtual Machine

When booting the image in QEMU you will see:

1. The GRUB bootloader with the refugiOS entry.
2. LightDM automatically logging in as the `refugios` user.
3. The XFCE desktop with:
   - Default desktop icons hidden.
   - The **"Completar instalación de refugiOS"** launcher on the desktop.
   - The welcome popup showing the disk size and recommended steps.

To complete the installation, connect to QEMU's virtual network (already enabled by default with NAT) and double-click the desktop launcher, or run in the terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

---

## 4. Flashing to Physical Device

Once the image has been verified in QEMU, you can flash it to your USB drive or external disk:

```bash
# MAKE SURE /dev/sdX is your real USB with 'lsblk'!
sudo dd if=refugios-base-16G.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

> [!WARNING]
> Always verify with `lsblk` or `fdisk -l` which is the real USB device before running `dd`. Writing to the wrong disk will destroy all data on that disk.

After flashing, the device will boot in UEFI on any compatible PC. On the first boot:

1. The **auto-expansion** service will resize the root partition to occupy all available space on the real disk.
2. The **welcome popup** will appear with basic instructions.
3. You can launch the **refugiOS installer** from the desktop icon.

---

## 5. Image Partition Layout

The generated image has the following GPT partition scheme:

| Partition | Size | Type | Format | Mount Point | Label/Flags |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 (EFI) | 512 MiB | EFI System Partition | FAT32 | `/boot/efi` | ESP (bootable) |
| 2 (ROOT) | Rest of the disk | Linux filesystem | ext4 | `/` | - |

The `/etc/fstab` file is automatically generated with the real UUIDs of both partitions to ensure correct mounting on any device.

---

## 6. Scripts and Services Injected into the Image

The build script injects the following components into the final image:

| Path | Type | Description |
| :--- | :--- | :--- |
| `/usr/local/bin/refugios-expand.sh` | Script | Disk auto-expansion on first boot |
| `/etc/systemd/system/refugios-expand.service` | systemd service | Runs auto-expansion and self-disables |
| `/usr/local/bin/refugios-install-wrapper.sh` | Script | Installer wrapper with connectivity check |
| `/etc/skel/Desktop/Instalar_refugiOS.desktop` | .desktop launcher | Installer icon on the desktop |
| `/usr/local/bin/refugios-trust-launcher.sh` | Script | Attempts to mark launcher as trusted |
| `/etc/xdg/autostart/refugios-desktop-trust.desktop` | Autostart | Runs trust script at session start |
| `/usr/local/bin/refugios-welcome.sh` | Script | Welcome popup on first boot |
| `/etc/xdg/autostart/refugios-welcome.desktop` | Autostart | Runs welcome popup at session start |
| `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml` | XFCE config | Hides default desktop icons |
| `/etc/lightdm/lightdm.conf.d/autologin.conf` | LightDM config | Autologin for the `refugios` user |
| `/etc/sudoers.d/refugios` | sudo config | Passwordless sudo for the `refugios` user |

---

## 7. Desktop Icon Trust Certification

> [!NOTE]
> Desktop icons (`.desktop` launchers) are now **automatically marked as trusted** by XFCE on first login. No manual intervention is required.

### How It Works

The build script includes `libglib2.0-bin` in the base system, which provides the `gio` command. On first login, the autostart script `refugios-trust-launcher.sh`:

1. Grants execution permissions to each launcher (`chmod +x`).
2. Calculates the SHA-256 checksum of the file and stores it in GIO metadata (`metadata::xfce-exe-checksum`).

This is the only metadata field that XFCE checks to consider a `.desktop` file as trusted. The installer (`install.py`) applies the same mechanism to any new icons it creates.

---

## 8. Comparison: Native Image vs. Live ISO with Persistence

| Aspect | Native Image (this method) | Live ISO with Persistence |
| :--- | :--- | :--- |
| **System base** | Native Debian Trixie | XUbuntu Live (SquashFS) |
| **Performance** | Superior (system installed directly) | Inferior (SquashFS indirection layer) |
| **USB wear** | Lower (no continuous write overlay) | Higher (constant writing to writable partition) |
| **Space used (base)** | ~7-8 GB | ~2-3 GB (compressed ISO) |
| **Customization** | Complete (real installed system) | Limited (only persistence layer) |
| **Creation complexity** | Medium (one automated command) | Low (Rufus/mkusb with existing ISO) |
| **Host requirements** | Debian-based + root | Any OS with Rufus/mkusb |
| **Autologin** | Yes (configured by default) | Yes (built into Live mode) |
| **Auto-expansion** | Yes (systemd, first boot) | No (fixed image size) |

---

## 9. Recommended Workflows

### Workflow A: Prepare a Single USB Drive

1. Build the image: `sudo bash scripts/build_refugios.sh 64G`
2. Test booting: `bash scripts/test_boot.sh 64G`
3. If it boots correctly, flash to USB: `sudo dd if=refugios-base-64G.img of=/dev/sdX bs=4M status=progress conv=fsync`
4. Boot from the USB and complete the installation.

### Workflow B: Prepare Multiple Identical Drives

1. Build the image once: `sudo bash scripts/build_refugios.sh 16G`
2. Test booting: `bash scripts/test_boot.sh`
3. Flash the same image to all USB drives:
   ```bash
   for dev in /dev/sdX /dev/sdY /dev/sdZ; do
       sudo dd if=refugios-base-16G.img of=$dev bs=4M status=progress conv=fsync
   done
   ```
4. Each unit will auto-expand on its first boot.

> [!TIP]
> For preparing large batches of devices, also check the **[Unit Cloning Guide](Cloning-Units-EN.md)** for more efficient methods like using `clonezilla` or hardware duplicators.

---

[Back to documentation](../README.md)
