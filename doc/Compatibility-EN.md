# Compatibility Table

This document details the compatibility status of **refugiOS** with different operating systems and hardware architectures.

## x86 Architecture (PC / Laptop)

| Operating System | Status | Notes |
| :--- | :--- | :--- |
| **XUbuntu 24.04 LTS** | ✅ Certified | Reference and recommended platform |
| **Xubuntu 25.10** | ✅ Certified | Must be retested for every new release |
| **Debian 11 (Bullseye)**| ⚠️ Issues | Requires adjustments. See [Technical Details](#debian-11-bullseye) |
| **Other distros (Debian/Ubuntu)** | 🧪 Untested | Testers wanted |

## ARM Architecture (Raspberry Pi)

| Device | Status | Raspberry OS Version | Notes |
| :--- | :--- | :--- | :--- |
| **Raspberry Pi 3B+** | ✅ Certified | April 13, 2026 | Recommended (RPi OS 64-bit) |
| **Raspberry Pi 4 / 5** | 🧪 Untested | - | Theoretically functional |
| **Raspberry Pi Zero 2W** | 🧪 Untested | - | Testers wanted |

---

## 🧪 Detailed Testing and Known Issues

### Debian 11 (Bullseye)
Installation has been tested on Debian 11, but several issues have been identified that require manual intervention or future correction:

*   **Flatpak:** The Flatpak package might not be installed automatically during the initial setup process.
*   **AppImages:** Errors have been reported regarding the dependencies required to run some AppImages.
*   **Issue Tracking:** These bugs are being tracked in **[Bug #10](https://github.com/Ganso/refugiOS/issues/10)** of the distribution.

---
[Back to README](../README.en.md)
