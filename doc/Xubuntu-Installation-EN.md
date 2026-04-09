# XUbuntu Installation Guide

This guide explains in detail how to prepare your refugiOS unit on a **XUbuntu** base from any operating system (Windows or Linux).

## 1. Choice of Hardware (The Support)

Before starting, the speed and lifespan of your refuge will depend on your hardware:

*   **Golden Recommendation:** Although a standard pendrive works, the ideal for good performance is a **pocket SSD drive** (or a USB adapter for M.2 NVMe drives). Cheap USB sticks wear out quickly under constant Linux use and their writing speed is very poor.
*   **Capacity and Content:**
    *   **16 GB (Absolute Minimum):** Base system + WikiMed + Basic Maps + Light AI. No space for Wikipedia.
    *   **32 GB (Balanced):** All of the above + "Mini" Wikipedia (only text or reduced images).
    *   **64 GB (Standard):** The ideal point! Includes **full Wikipedia with images**, Phi-4-mini AI model, and detailed maps.
    *   **128 GB or more:** Allows massive libraries (Survivor Library), world maps, and multiple AI models.

> [!TIP]
> **Buying Tips (What to look for?):**
> *   **USB Version:** Always look for **USB 3.0, 3.1, or 3.2** (sometimes marked as "Gen 1" or "Gen 2"). The connector is usually blue or red inside.
> *   **Speed:** On the box, look for read speeds above **150 MB/s** and write speeds above **50 MB/s**.
> *   **Format:** Those with metal casings dissipate heat better during intensive use.
>
> **⚠️ What to avoid:**
> *   **USB 2.0:** It is desperately slow to run an operating system. A boot that takes 30 seconds on USB 3.0 can take 10 minutes on USB 2.0.
> *   **Unknown Brands:** Flee from "too good to be true" offers of 1 TB for €10; they are usually scams with tiny real capacity.
>
> **Backup Strategy:**
> If you have old or smaller pendrives (16 GB), don't throw them away. You can leave them as **backup units** in a backpack, first aid kit, or vehicle with the base system. Always carry "the good one" (fast SSD or USB 3.2) as your main unit.

### How to distinguish an SSD from a Pendrive?
It's easy to confuse them by name, but their performance is worlds apart:
*   **Pendrive (USB Memory):** It's the size of a thumb, very light and cheap. It gets very hot and its speed drops drastically after 5 minutes of use.
*   **Pocket SSD:** It's somewhat larger (like a lighter or a matchbox), usually has a metal case and speeds that don't drop below 400 MB/s. It's a real disk drive, but miniaturized.

### What to ask for in the store (or search on Amazon)
If you go to a physical store or search online, use these magic words not to fail:
*   **In physical store:** *"I want an external pocket SSD drive, that is USB 3.2 and at least 64GB (or 128GB), with read speed above 400 MB/s"*.
*   **In online stores:** Search for *"Portable SSD 128GB USB 3.2"* or *"External solid state unit USB-C"*. Make sure the description says **"SSD"** and not just "Flash Drive" or "USB Stick".

### Reference Devices and Budgets (Spain)

To facilitate the choice, here are three recommended configurations. Keep in mind that technology prices are very volatile and serve only as a guide, and that at the time of writing this (March/April 2026) prices are undergoing an upward trend:

1.  **Base Option (Economic / Replicas):**
    *   **What it is:** A 32GB or 64GB metallic USB 3.2 pendrive (e.g., SanDisk Ultra Luxe or Kingston DataTraveler Kyson).
    *   **What for:** Ideal for having **multiple cheap security replicas** of the base system in backpacks, vehicles, or kits. Not recommended for intensive daily use.
    *   **Real 2026 Price:** Between **€8 and €20**.
    *   *Note:* A standard 64GB model is found for about **€10**. 32GB versions start at **€14**, going up to **€15-€25** for the fastest 64GB. Plastic models are cheaper (**€8**), but their low durability doesn't justify the small saving.

2.  **Intermediate Option (SATA Adapter):**
    *   **What it is:** A USB to SATA III adapter (cable or casing) to connect existing 2.5" or 3.5" HDD or SSD disks.
    *   **What for:** The best way to **recycle old computer disks** to have a high-speed, high-capacity refugiOS for day-to-day use without spending much. An SSD will give us a read and write speed comparable to a modern computer, while a well-cared-for HDD can have enormous durability (although we'll have to be more careful with bumps or magnetic fields).
    *   **Real 2026 Price:** Between **€10 and €20**, plus the price of the hard drive we already have.
    *   *Note:* Basic aluminum casings are found between **€5 and €10**. High-fidelity cable adapters with UASP support range between **€15 and €20**.

3.  **Premium Option (Main Unit):**
    *   **What it is:** A dedicated 250GB Portable SSD or a DIY assembly (NVMe + Casing).
    *   **What for:** As a **high-performance main unit**. Essential for intensive use of complex AI models, full Wikipedia with images, and detailed world maps.
    *   **Real 2026 Price:** Between **€60 and €90**.
    *   *Note:* "Assembled" premium models usually start at 500GB (**€100-€150**). The real 250GB option is around **€65**. Assembling an NVMe module by parts can cost **€80-€90**, being more expensive but allowing future upgrades.

#### Performance and Experience Comparison (2026)

| Use Profile | Capacity | Investment (Est.) | Installation Time | User Experience |
| :--- | :--- | :--- | :--- | :--- |
| **OS Distribution** | 32 GB - 64 GB | 10 € - 20 € | A full afternoon | With continuous waits |
| **SSD Recycling** | 128 GB - 256 GB | 15 € (Adap. only) | ~1 hour | Fluid (almost native) |
| **High Performance** | 250 GB | 60 € - 90 € | < 45 minutes | Responsive (like local) |

> [!IMPORTANT]
> This price ecosystem reflects that the 2026 market penalizes lower capacities. The price difference between a slow pendrive and a 250GB SSD is today one of the most important value gaps for the end user.

---

## 2. Base Image Download (The Software)

We use light versions of Xubuntu to maximize available free space:

*   [**Xubuntu 24.04 LTS (Recommended)**](https://xubuntu.org/): The most stable option with guaranteed support for years.
*   [**Xubuntu 25.10 (Latest version)**](https://xubuntu.org/): If you prefer to have more modern kernels for very new hardware, although with a shorter support cycle.
*   **Notice:** Always download the **"Minimal"** variant to save about 2 GB of space by removing unnecessary programs (games, heavy office software, etc.).

---

## 3. Creation of the Boot Drive

There are two main ways to configure the system. Read carefully:

### Option A: USB "Live" with Persistence (Recommended)

The system resides safely in an inert image (SquashFS) and changes are saved in the `writable` partition. This avoids excessive memory wear and protects your host computer.

*   **From Windows:** Use [**Rufus**](https://rufus.ie/). When choosing the ISO, drag the **"Persistent partition size"** slider to the maximum possible (leaving a little room).
*   **From Ubuntu:**
    You have two main ways to prepare the USB:
    1.  **Option 1: [Startup Disk Creator (Official Guide)](https://help.ubuntu.com/stable/ubuntu-help/addremove-creator.html)**. It is the native and simplest tool if you don't need advanced persistence.
    2.  **Option 2: mkusb (Advanced users)**. This is the recommended option to ensure that persistence works correctly and to save your changes in refugiOS.
        ```bash
        sudo add-apt-repository ppa:mkusb/ppa
        sudo apt update
        sudo apt install mkusb usb-pack-efi
        ```

*   **From Debian:**
    Because modern versions of Debian (12, 13 and above) have strict security policies that block old repositories, we will perform a manual installation:
    1. **Installation of necessary packages:**
       Download the `.deb` files (always search for the most recent version) of **dus**, **mkusb-common**, **mkusb-nox**, and **usb-pack-efi** from the [official mkusb repository](https://ppa.launchpad.net/mkusb/ppa/ubuntu/pool/main/m/mkusb/).
       
       Open a terminal in your downloads folder and install them all at once:
       ```bash
       sudo apt update
       sudo apt install ./dus_*.deb ./mkusb-common_*.deb ./mkusb-nox_*.deb ./usb-pack-efi_*.deb
       ```

#### Guide for using mkusb/dus (Common for Ubuntu and Debian)

If you have chosen the option to install **mkusb**, follow these exact steps in the tool:

1.  **Start:** Run `sudo dus` in the terminal.
2.  **Action:** Select `i: Install (make a boot device)`.
3.  **Image Selection:** Choose the Xubuntu `.iso` file you have downloaded.
4.  **Target Selection:** Mark your pendrive. (**Attention!** Check the size to make sure you are not marking your main hard drive).
5.  **Method (Tool):** Select `p: 'dus-Persistent', classic dus method`.
6.  **Additional Options:** For any choice not indicated here, always select **"Use defaults"**.
7.  **Persistence Space:** Here you must make a decision:
    - **100% (Recommended):** If you want to use the entire pendrive for refugiOS and its files.
    - **50%:** If you want half of the USB to be a common data partition (`usbdata`) visible from any operating system (this data will **not** be encrypted, so you should not have personal information there).
8.  **Confirmation:** A final warning screen will appear (red/orange background). Select **Go (Yes)** and press OK.

*   **Other Linux (Manual with `dd`): (not recommended)**
    If you record the image directly, you must create the data partition and configure the boot manually:
    ```bash
    # 1. Record ISO (sdX is your USB)
    sudo dd if=xubuntu-minimal.iso of=/dev/sdX bs=4M status=progress
    # 2. Create partition with fdisk
    sudo fdisk /dev/sdX
    # (Press 'n' for new, 'p' primary, '3' for the number, 'Enter' to everything and 'w' to save)
    # 3. Format with the mandatory label "writable"
    sudo mkfs.ext4 -L writable /dev/sdX3
    ```
    > **Important:** When booting for the first time from a USB created with `dd`, you will see the boot menu (GRUB). You must press the **`e`** key, look for the `linux` line, and add the word `persistent` before the three dashes `---`. Press **F10** to boot.
    > 
    > To avoid doing this every time you will have to edit the boot of the portable system, a technical process that we detail in **[Section 3 of the Virtualization Guide](Virtualization-Guide-EN.md#3-stabilization-of-the-persistence-at-boot-grub-within-the-image)**. Therefore, it is recommended to use Rufus or mkusb unless you know very well what you are doing and feel comfortable with the command line.

### Option B: Native Installation (Experts only)

We do not recommend this method on conventional USBs because Linux "journaling" will destroy them in a few months. **Use it only if you have an SSD via USB.**

1.  Create a normal installer USB.
2.  **TECHNICAL ADVICE:** Disconnect the internal disks of your PC before starting. If you don't, the Ubuntu installer could "hijack" your Windows boot and mess up the start of your main computer.
3.  Install Xubuntu choosing the USB SSD as target and activate full disk encryption (LUKS) if you wish.

---

## 4. Testing, Virtualization, and Dump

If you want to mount RefugiOS on a local disk image before touching the physical pendrive, or if you prefer to test that everything works correctly in a virtual machine before restarting your PC:

*   👉 **[Virtualization Guide and Pendrive Preparation](Virtualization-Guide-EN.md)**

This comprehensive guide will teach you how to create an `.img` image, install the system inside a VM (such as VirtualBox or QEMU), and dump the final result to the USB safely.

This is the recommended option for advanced users, as it allows for much faster local work, and then dumping the final result to the USB safely. It is also perfect if you want to prepare a batch of USB devices of similar size.

---

## 5. First Boot and refugiOS Installation

Turn off your PC and boot from the USB (F12/F8/Esc).

1.  **Keyboard Configuration (Spanish):** 
    By default, the "Live" session starts in English. To set the keyboard in Spanish:
    *   Click on the **applications menu** (top left corner).
    *   Go to **Settings** -> **Keyboard**.
    *   On the **Layout** tab, disable the option **"Use system defaults"**.
    *   Click on **+ Add**, search for **Spanish**, and click OK.
    *   (Optional) You can move "Spanish" to the top or delete "English" to make it the default keyboard.
    
2.  **Launch the Installer:** Once inside the Xubuntu desktop, connect to the network and paste this into the terminal:
    ```bash
    sudo apt install curl -y
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
    ```
2.  **Configuration:** The wizard will detect your hardware and suggest the best ZIM libraries for your capacity.

Upon completion, your refugiOS device will be **completely autonomous**, private, and capable of working without Internet forever.

---

## Annex: Compatibility with Old Computers (BIOS / MBR)

If you try to boot refugiOS on an old computer (approximately pre-2012) and the USB does not appear in the boot menu or is not recognized as a boot drive, your machine likely uses the traditional **BIOS** system instead of the modern **UEFI**.

In these cases, the USB must be configured with an **MBR (Master Boot Record) Partition Table** to be detected.

### Solutions according to your creation tool:

#### 1. From Windows (Rufus)
Rufus is the tool that offers the most manual control over this aspect. To force compatibility with old equipment:
*   In **Partition scheme**, select **MBR**.
*   In **Target system**, select **BIOS (or UEFI-CSM)**.
*   The rest of the options (Persistence, ISO) remain the same.

#### 2. From Linux (mkusb / dus)
**mkusb** is the most robust tool for old hardware. By default, it creates **hybrid** drives that contain both UEFI and BIOS (MBR) boot, so it usually works "at first" on almost any computer without additional adjustments.
*   If the equipment is extremely old, make sure to choose the method `p: 'dus-Persistent', classic dus method`, as it is the one that best manages legacy compatibility.

#### 3. Startup Disk Creator / `dd` command
These tools work by literally cloning the ISO image.
*   Since the official Xubuntu images are **isohybrid**, they include basic BIOS and UEFI support out of the box. 
*   However, if your old motherboard has a very strict boot implementation, these tools could fail. In that case, the ultimate solution is to use **mkusb**.

> [!TIP]
> **How to know if my PC needs MBR?**
> If when turning on the computer you see the brand logo and a text that says *"Press F2 for Setup"* or *"F12 for Boot Menu"*, but that configuration interface looks like something from the late 90s (text only, no mouse support), you almost certainly need a drive prepared for **BIOS/MBR**.
