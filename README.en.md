# refugiOS - Your Digital Refuge and Survival Library

<p align="center">
  <a href="README.md">Español 🇪🇸</a> | <strong>English 🇬🇧🇺🇸</strong>
</p>

<p align="center">
  <img src="logo/refugiOS.png" alt="refugiOS logo"><br />
  <img src="https://img.shields.io/badge/Status-Development-green.svg" alt="Project Status">
  <img src="https://img.shields.io/badge/Version-0.10-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Paradigm-Offline_First-orange.svg" alt="Offline First">
  <img src="https://img.shields.io/badge/AI-Llamafile_(Local)-purple.svg" alt="Offline AI">
  <img src="https://img.shields.io/badge/Raspberry_Pi-Certified-red.svg" alt="Raspberry Pi">
</p>

> [!WARNING]
> **Project Status:** refugiOS is currently in its **first Alpha version**. It is an actively developing project and there is still a long way to go: internationalization of the documentation, bug fixing, and the implementation of the features detailed in the roadmap.

---

## 📖 What is refugiOS?

**refugiOS** is a portable operating system designed for emergency situations, lack of Internet connectivity, or extreme privacy needs.

Unlike other complex solutions, **refugiOS turns any ordinary computer (even an old one) into a complete information station** that boots directly from a USB drive.

It also works on **Raspberry Pi**, turning it into a compact, silent, and low-power information station.

It is a tool designed to have all vital knowledge, maps, and documents at hand in a safe, private, and fully functional way without depending on the cloud.

## ✨ Main Features

*   **⚡ Boots on any PC (Plug-and-play):** You don't need to install anything on the computer you find. You connect the USB, turn on the machine, and your digital refuge is already running at full capacity.
*   **🍓 Native Raspberry Pi Support:** Certified installation on Raspberry Pi 3B+. The installer automatically detects the ARM architecture and adapts all decisions (APT packages, graphics rendering, etc.).
*   **📚 Universal Offline Knowledge:** Includes complete copies of Wikipedia, WikiMed (medicine), survival encyclopedias, and trade guides thanks to *Kiwix* technology.
*   **🤖 Private Artificial Intelligence:** Incorporate an assistant that works 100% locally, without Internet. It can help you solve technical, medical, or translation problems using only the power of your computer.
*   **🗺️ Maps and GPS Navigation:** Detailed maps of the entire world via *Organic Maps*. You can search for routes and points of interest (fountains, hospitals, shelters) without emitting any network signal.
*   **🔒 Secure File Vault:** Professional encryption system to store your most important documents (passports, titles, photos) protected by a master password.
*   **🌐 Adapted to Your Language:** The system automatically configures in your language (Spanish or English), downloading only the dictionaries and help files you need.
*   You can see in the **[Applications and Roadmap](doc/Modules-and-Roadmap-EN.md)** section the current status of the project, with the modules that are already implemented and those that will be added in the future.

## 📸 Screenshots

| Element | Screenshot |
| :--- | :--- |
| **Main Interface** | ![Main menu](screenshots/Menu+Bobeda.png)<br>*Main menu with an open vault* |
| **Knowledge** | ![Medical encyclopedia](screenshots/Medicina.png)<br>*Medical encyclopedia (WikiMed)* |
| **Navigation** | ![Cartography](screenshots/Mapas.png)<br>*Cartography and offline navigation* |
| **Assistant** | ![Local AI](screenshots/IA%20local.png)<br>*Local Artificial Intelligence* |

### 📺 Demo Video

<p align="center">
  <a href="https://www.youtube.com/watch?v=VrP8VIxQZGg">
    <img src="https://img.youtube.com/vi/VrP8VIxQZGg/maxresdefault.jpg" alt="refugiOS in action" width="800">
  </a>
  <br>
  <em>refugiOS running on a 2018 Microsoft Surface, booted from a 16GB USB drive and completely offline</em>
</p>

## 🚀 Quick Installation

### 💻 On XUbuntu (PC / Laptop)

If you already have a USB with XUbuntu freshly installed, you just need to connect the team to the Internet once and run this command in the terminal:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

> [!IMPORTANT] 
> **Don't have the XUbuntu USB ready yet?** 
> If you're starting from scratch, first follow our **[XUbuntu Installation Guide](doc/Xubuntu-Installation-EN.md)** to prepare your pendrive from Windows or Linux.

### 🍓 On Raspberry Pi

First install Raspberry Pi OS with the official tool **[Raspberry Pi Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager)** and then run the same installer:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

The installer will automatically detect that you are on a Raspberry Pi and adapt everything. See the **[Raspberry Pi Installation Guide](doc/Raspberry-Pi-Installation-EN.md)** for details and hardware recommendations.

> [!NOTE] 
> The installer will guide you step by step and ask you what content you want to include based on your storage size.

> [!TIP]
> **Already have your first USB drive ready?** Once you've tried it and configured it to your liking, we recommend **[cloning it to another unit](doc/Cloning-Units-EN.md)** to have a backup or to give copies to your loved ones.

> [!NOTE]
> **Want to try it quickly without touching a USB drive?** If you have experience with virtual machines, you can mount refugiOS on a virtual disk image and boot it with QEMU or VirtualBox. See our **[Virtualization Guide](doc/Virtualization-Guide-EN.md)** for detailed steps.


## 📱 Certified Platforms

| Platform | Status | Notes |
| :--- | :--- | :--- |
| **XUbuntu 24.04 LTS** | ✅ Certified | Reference platform |
| **Xubuntu 25.10** | ✅ Certified | Needs retesting every new release |
| **Raspberry Pi 3B+** | ✅ Certified | Raspberry Pi OS 64-bit, Wayland |
| **Raspberry Pi 4 / 5** | 🧪 Untested (theoretically functional) | Testers wanted |
| **Raspberry Pi Zero 2W** | 🧪 Untested | Testers wanted |
| **Other Debian-based distros** | 🧪 Untested | Testers wanted |

## 📚 Detailed Documentation

To learn more about how refugiOS works and how to get the most out of it, consult the guides in the `/doc/` directory:

*   **[XUbuntu Installation](doc/Xubuntu-Installation-EN.md):** How to prepare your XUbuntu USB from Windows or Linux.
*   **[Raspberry Pi Installation](doc/Raspberry-Pi-Installation-EN.md):** Specific guide for Raspberry Pi with Raspberry Pi OS.
*   **[Vision and User Experience](doc/Vision-and-User-Experience-EN.md):** The purpose of the project and what to expect when using it.
*   **[Comparison of Solutions](doc/Comparison-of-Solutions-EN.md):** Why refugiOS is different from other alternatives.
*   **[Applications and Roadmap](doc/Modules-and-Roadmap-EN.md):** Information about Kiwix, Maps, and Artificial Intelligence.
*   **[System Architecture](doc/System-Architecture-EN.md):** Technical details about the Linux base and its performance.
*   **[Security Vaults](doc/Security-Vaults-EN.md):** How the encryption of your personal files works.
*   **[Unit Cloning](doc/Cloning-Units-EN.md):** How to make exact copies of your USB on Windows or Linux.


---

## 🗃️ Acknowledgements and Sources

Special thanks to [Felipe Monge "PlayOnRetro"](https://x.com/PlayOnRetro) for the logo design.

refugiOS is possible thanks to the incredible work of open source projects like:
*   [Xubuntu](https://xubuntu.org/) and the Ubuntu community for the operating system base.
*   [Raspberry Pi Foundation](https://www.raspberrypi.com/) for the hardware and ARM software ecosystem.
*   [Kiwix](https://www.kiwix.org/) and the [Wikimedia Foundation](https://wikimediafoundation.org/) for offline access to universal knowledge.
*   [Mozilla Ocho](https://github.com/Mozilla-Ocho/llamafile) for the **Llamafile** inference engine.
*   [HuggingFace](https://huggingface.co/) and [bartowski](https://huggingface.co/bartowski) for the excellent AI model quantizations.
*   **Phi-4-mini** (Microsoft) and **Qwen3** (Alibaba-Qwen) language models.
*   [Organic Maps](https://organicmaps.app/) and [OpenStreetMap](https://www.openstreetmap.org/) contributors for offline mapping.
*   [Aria2](https://aria2.github.io/) for high-efficiency downloads.
*   [Flatpak](https://flatpak.org/) and [Flathub](https://flathub.org/) for modern application distribution.
*   [Cryptsetup / LUKS](https://gitlab.com/cryptsetup/cryptsetup) for personal data security and encryption.

---
*(refugiOS is an open source initiative for digital resilience. Currently in Alpha phase, we are looking for collaborators to internationalize the documentation, migrate it to wiki format, and polish the user experience according to our [Roadmap](doc/Modules-and-Roadmap-EN.md)).*
