# Vision and User Experience

This document explains what **refugiOS** is, its purpose, and the experience of using it, both during preparation and in an emergency situation.

## 1. What is refugiOS?

The name combines "Refugio" (Refuge) and "OS" (Operating System). We want it to be a **digital refuge**: a safe place to store knowledge, maps, and important documents for when normal networks (Internet, electricity, telephony) fail.

It is a tool designed to always work **offline** (100% offline).

### Main Use Cases:
*   **Natural Disasters:** Earthquakes or floods that cut off communications for weeks.
*   **Prolonged Blackouts:** Power or data network failures.
*   **Remote Areas:** Places without coverage where you need medical guides or maps.
*   **Extreme Privacy:** For people who need to protect their personal information with professional encryption.

In summary: refugiOS turns any computer (even an old or salvaged one) into a completely independent information and survival center.

---

## 2. Preparation (Before the Crisis)

The process of creating the device is simple and designed so that anyone can do it at home with peace of mind:

1.  **The Support:** You only need a good quality USB drive or portable SSD.
2.  **The Boot:** You burn a Linux image (Xubuntu) onto the USB following our guide.
3.  **The Installer:** You boot the computer from that USB and run a single command.
4.  **Guided Configuration:** A simple menu will appear asking:
    *   Your preferred language.
    *   What content you want to download (full Wikipedia, medical manuals, etc.) according to your USB's capacity.
    *   What maps of which regions of the world you need.
5.  **Your Personal Vault:** The system will help you create a secure folder with a password so you can store your photos, passports, medical prescriptions, and important documents.

---

## 3. Use in an Emergency Situation

When a real problem occurs, refugiOS is designed to be fast, simple, and without technical complications:

1.  **Universal Boot:** You connect the USB to any working computer (even a borrowed or old one powered by a solar battery).
2.  **Clean Desktop:** Upon turning it on, you enter a simple desktop directly. It won't ask for Wi-Fi passwords or weird configurations.
3.  **Clear and Direct Icons:** On the desktop, you'll see large buttons for what you need:
    *   **"Medical Encyclopedia":** To know how to treat a wound or identify a disease (via [Wikipedia](https://en.wikipedia.org/)/[WikiMed](https://www.kiwix.org/)).
    *   **"Maps":** To find water sources, shelters, or hospitals without using the Internet or sending your position to anyone (via [Organic Maps](https://organicmaps.app/)).
    *   **"AI Assistant":** An assistant you can ask complex questions (e.g., "How to purify water?") and it will answer using only the power of that computer (via [Llamafile](https://github.com/Mozilla-Ocho/llamafile) and the [Phi-4-mini](https://huggingface.co/microsoft/Phi-4-mini-instruct) model).
    *   **"My Documents":** You enter your password and your personal files appear to identify yourself or ask for help.

refugiOS is, quite simply, your digital life insurance when the connected world stops working.
