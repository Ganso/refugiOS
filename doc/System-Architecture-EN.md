# System Architecture

To guarantee the reliability of refugiOS in critical situations, we have made design decisions focused on lightness, compatibility, and ease of use, without sacrificing the power of Linux.

## 1. Base System

*   **Operating System:** Linux.
*   **Distribution:** [**Xubuntu LTS**](https://xubuntu.org/), an official Ubuntu version using the [**XFCE**](https://www.xfce.org/) desktop.
*   **Performance:** XFCE is ideal for old devices or those with limited resources. A freshly booted system uses **less than 1 GB of RAM**, which saves battery on laptops and allows it to run smoothly on almost any hardware.

### Recommended Versions:
*   **Xubuntu 24.04 LTS:** Offers long-term stability and guaranteed technical support for years.
*   **Xubuntu 25.10 Minimal:** This is the "clean" version that does not include unnecessary programs (games, heavy players, etc.), allowing us to save about 2 GB of extra space for useful content.

Our philosophy is to use a **standard** system. This means any person with basic Linux knowledge will be able to easily repair or improve the system without needing rare or proprietary tools.

---

## 2. Languages and Adaptation (Internationalization)

refugiOS is designed to be global. The installer automatically detects your system's language or allows you to choose it manually.

We use native Ubuntu tools (`check-language-support`) so that during preparation, the system downloads only what is necessary:
*   Local keyboard configuration.
*   App and system translations.
*   Dictionaries for document readers.
*   Compatible languages for the AI assistant.

In this way, the system adapts completely to your region without occupying unnecessary space with languages you won't use.

---

## 3. Software Philosophy: Simplicity and Portability

Unlike other projects that use complex virtualization systems or heavy "containers," refugiOS relies on direct and portable applications:

*   **AppImages:** These are applications that don't need installation. Everything needed for them to work is inside a single file.
*   **Static Executables:** Such as the AI engine ([Llamafile](https://github.com/Mozilla-Ocho/llamafile)), which works by simply double-clicking, without complicated configurations.
*   **Security Vaults:** To protect your personal files, we use the Linux disk encryption standard ([**LUKS**](https://gitlab.com/cryptsetup/cryptsetup)), which is extremely secure and compatible.

This approach ensures that the software is robust, easy to move between devices, and consumes the minimum possible resources from your computer.
