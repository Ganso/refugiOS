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

To make the system easy to use, refugiOS provides a **Secure Vault Manager** — a single interactive application accessible from the desktop icon labeled "Secure Vault Manager".

When you open the Vault Manager, you will see a list of all your existing vaults, each showing its current state (**OPEN** or **CLOSED**) and its size. From this main menu you can:

1.  **Select an existing vault** — opens a contextual submenu with the actions available for that vault depending on its state:
    *   If the vault is **closed**: you can **Open** it (enter the password and an icon will automatically appear on the desktop for direct access to your files) or **Delete** it permanently.
    *   If the vault is **open**: you can **Close** it (the desktop icon will disappear and your files will be protected by professional LUKS encryption again).

2.  **Create a new vault** — a step-by-step wizard that will detect if you have USB drives connected and suggest a size based on your data. You can choose a custom name for each vault. When finished, the system can automatically import your files from the USB.

**Security tip:** Always close your vault as soon as you finish using it. While it is open, anyone with physical access to your computer could see the files.
