# Security Vaults (Security and Encryption)

In crisis situations or during travel, it is possible that your refugiOS device could be confiscated or stolen. If you store document photos (ID cards, passports), medical information, or bank keys unprotected on a USB, anyone who finds it will have total access to your private life.

To prevent this, refugiOS includes a **Secure Vaults** system that keeps your personal files encrypted and hidden.

## What is a Secure Vault?

Instead of protecting the entire USB drive with a password (which can be slow or cause compatibility issues), refugiOS uses "encrypted containers."

A container is a special file (for example, `my_data.img`) that works like a safe. You can only see what's inside if you know the correct password.

### Key Features:
*   **Professional Standard:** We use [**LUKS**](https://gitlab.com/cryptsetup/cryptsetup) (Linux Unified Key Setup), the same encryption system used by governments and companies on Linux. It is extremely secure.
*   **Modularity:** You can have several different vaults (one for medical issues, another for legal documents) with different passwords.
*   **Speed:** You can open and close your files in seconds.

---

## How Vaults Work in refugiOS

To make the system easy to use, we have created three direct buttons on your desktop:

1.  **Create Vault:**
    The first time you use the system, this button will guide you through creating your secure file. It will ask you to choose a **strong password** (don't forget it; if you lose it, you won't be able to recover your files!). The system will create a reserved space of about 3 GB for your documents.

2.  **Open Vault:**
    By double-clicking, a small window will open asking for your password. If it is correct, a folder called **MY_SECRET_DATA** will appear on your desktop. There you can copy, paste, and edit your files normally.

3.  **Close Vault:**
    When you finish working, press this button. The folder will automatically disappear from the desktop and your files will be encrypted and protected again. No one will be able to see them even if they connect the USB to another computer.

**Security tip:** Always close your vault as soon as you finish using it. While it is open, anyone with physical access to your computer could see the files.
