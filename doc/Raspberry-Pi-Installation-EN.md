# Raspberry Pi Installation Guide

This guide explains how to install **refugiOS** on a Raspberry Pi, from scratch to having the system fully functional.

> [!NOTE]
> **Certified Platforms:** This guide has been tested and certified on **Raspberry Pi 3B+** with Raspberry Pi OS (64-bit, Wayland). Testers with other models are wanted. If you try it on a different model, open an issue or contact the project!

---

## 1. Necessary Hardware

### Raspberry Pi
- **Certified:** Raspberry Pi 3B+ (1 GB RAM)
- **Recommended:** Raspberry Pi 4 or higher (≥2 GB RAM) for better AI performance and no graphical limitations
- **Pending Testing:** Raspberry Pi 2, 3A, Zero 2W, 5

> [!IMPORTANT]
> With Raspberry Pi versions prior to 4, **Organic Maps** will work via software rendering (automatic). The experience may be slower, but it is functional.

### Storage Media

The choice of storage is critical on Raspberry Pi, as cheap microSD cards degrade quickly under the constant use of an operating system:

*   **Golden Recommendation:** An **SSD with USB adapter** or an **SSD mounted on an NVMe HAT** will give the best experience. Cheap microSD cards wear out in a few months of intensive use.
*   **Capacity:**
    *   **16 GB (Minimum):** Base system + WikiMed + Minimal AI. No space for Wikipedia.
    *   **32 GB (Balanced):** All of the above + Light Wikipedia.
    *   **64 GB (Standard):** The ideal point. Includes full Wikipedia (text) and basic AI model.
    *   **128 GB or more:** Allows WikiHow, Wikipedia with images, and multiple AI models.

> [!TIP]
> Always use an **A2 Class microSD card** (e.g., SanDisk Extreme, Samsung Pro Endurance) if you don't have an SSD. They are the only ones designed to withstand continuous random read/write use of an operating system.

---

## 2. Base Operating System Installation

### Step 1: Raspberry Pi Imager (Required)

The official and simplest way to install Raspberry Pi OS is using the official **Raspberry Pi Imager** tool:

👉 **[Official Raspberry Pi Imager Guide](https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager)**

1.  Download and install **Raspberry Pi Imager** on your PC (Windows, Mac, or Linux).
2.  Connect your microSD card or USB SSD to your PC.
3.  In Imager, select:
    *   **Device:** Your Raspberry Pi model
    *   **Operating System:** `Raspberry Pi OS (64-bit)` — the full desktop version with graphical environment
    *   **Storage:** Your card/SSD
4.  Click **Next** and configure the custom options:
    *   Hostname, username, and password
    *   Your Wi-Fi network (if you use it)
    *   Enable SSH if you need it
5.  Confirm and wait for the writing to finish.

> [!TIP]
> If you want to use a Wi-Fi network, it is much more convenient to configure it from Imager before recording than to do it later from the Raspberry Pi itself.

### Step 2: First Boot

1.  Insert the card/SSD into the Raspberry Pi and turn it on.
2.  The system will boot directly to the desktop (if you used the desktop edition).
3.  Configure the language and keyboard if the welcome wizard prompts you.

---

## 3. refugiOS Installation

Once inside the Raspberry Pi OS desktop, open a terminal and run:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

The installer will automatically detect the ARM architecture and adapt all decisions:
- It will use `kiwix` via APT instead of AppImage (x86 only).
- It will configure Organic Maps for software rendering if it's a RPi version prior to 4.
- It will adjust the default selection of modules according to available RAM and space.

---

## 4. Differences from XUbuntu Installation

| Feature | Raspberry Pi | XUbuntu |
| :--- | :--- | :--- |
| **Kiwix Desktop** | APT (`kiwix`) | AppImage or Flatpak |
| **Organic Maps** | Software rendering on RPi <4, native GPU on RPi 4+ | Native GPU |
| **Security Vaults** | ✅ Functional | ✅ Functional |
| **AI Assistant** | ⚠ Limited by RAM (minimal model recommended on 3B+) | ✅ Complete |
| **Window Manager** | Wayfire / Labwc (Wayland) | XFCE (X11 or Wayland) |

---

## 5. Keyboard Configuration in Spanish

If the system started in English and you need the Spanish keyboard:

1.  Click on the applications menu.
2.  Go to **Preferences** → **Raspberry Pi Configuration** → **Localisation** tab.
3.  Set **Locale**, **Keyboard**, and **Timezone** according to your country.
4.  Restart when prompted.

---

## 6. Performance Notes

*   **RAM Memory:** With only 1 GB (Raspberry Pi 3B+), the minimal AI model (Qwen2.5-0.5B) is recommended. The basic model (Phi-4-mini) may work but with active swap and noticeable slowness.
*   **Swap:** To use larger AI models, you can expand the swap:
    ```bash
    sudo dphys-swapfile swapoff
    sudo nano /etc/dphys-swapfile  # Change CONF_SWAPSIZE=100 to 2048
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    ```
*   **Kiwix:** Works correctly. Needs a few additional seconds for indexing the first time it opens a large encyclopedia.

---

## 7. Offline Knowledge (ZIM)

The process for downloading and installing knowledge bases (Wikipedia, WikiMed, WikiHow) is identical to XUbuntu. See the [XUbuntu Installation Guide](Xubuntu-Installation-EN.md) for content selection details.

Upon completion, your Raspberry Pi will run **refugiOS** **completely autonomously**, without Internet, with encyclopedic knowledge, offline maps, and local artificial intelligence.
