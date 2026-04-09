# Applications, Included Content, and Development Roadmap

refugiOS includes a selection of tools designed to work entirely without an Internet connection. Below are the modules currently available and those we plan to add soon.

> [!IMPORTANT]
> **Internationalization (i18n):** Currently, both the installer and documentation are available **only in Spanish**. Translation to English will be undertaken soon and, later, to other languages depending on community interest.
>
> **Documentation Migration:** We are in the process of migrating all technical and user documentation to the **GitHub Wiki** format to facilitate consultation and collaboration.

---

## 🚀 Current Modules (Already Available)

These components are installed automatically or through the welcome wizard:

### 1. Offline Library and Encyclopedias ([Kiwix](https://www.kiwix.org/))
Access to massive databases using the ZIM format.
*   **Contents:** [Wikipedia](https://en.wikipedia.org/) (General), [WikiMed](https://www.kiwix.org/en/get-kiwix/download-content/) (Medicine), [WikiHow](https://www.wikihow.com/) (Practical guides).
*   **Language:** 🌐 **Multilingual.** The installer downloads the files specifically in the language you choose (en, es, fr, etc.).

### 2. Maps and Navigation ([Organic Maps](https://organicmaps.app/))
Detailed vector maps with offline search and routing.
*   **Contents:** Maps of cities, trails, water sources, and hospitals.
*   **Language:** 🌐 **Multilingual.** The interface and map names adapt to your region.

### 3. Artificial Intelligence Assistant ([Llamafile](https://github.com/Mozilla-Ocho/llamafile))
Private smart assistant that works 100% on your local computer. Available in four levels according to device capacity:
*   ⚪ **Minimal:** [Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) (0.5B) — ~0.5 GB. For devices with very limited resources (min. 1 GB RAM).
*   🟢 **Basic:** [Phi-4-mini](https://huggingface.co/microsoft/Phi-4-mini-instruct) (3.8B) — ~2.5 GB. Works on any PC with 4 GB of RAM.
*   🟡 **Medium:** [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) (8B) — ~5 GB. For modern laptops with 8 GB of RAM.
*   🔴 **Advanced:** [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) (14B) — ~9 GB. For powerful PCs with 16 GB of RAM.
*   **Automatic Selector:** When launching the assistant, a script detects the available RAM and recommends the appropriate model.
*   **Language:** 🌐 **Multilingual.** All models understand and respond in more than 20 languages.

### 4. Cryptographic Vaults (LUKS)
Secure and encrypted storage system for sensitive data.
*   **Status:** 🧪 **Proof of Concept (PoC).** The system is functional and uses the LUKS industrial standard, but it is in a primitive phase of usability.
*   **Current Limitations:** Currently only supports a fixed-size vault.
*   **Next Improvements:** Support for multiple vaults, variable sizes, and a more intuitive management interface.

### 5. Standard Work Tools
Essential programs for daily life, adapted for maximum compatibility.
*   **Office and Multimedia:** [LibreOffice](https://www.libreoffice.org/), [VLC](https://www.videolan.org/), [Evince](https://wiki.gnome.org/Apps/Evince) (PDF).
*   **System and Navigation:** [Epiphany Browser](https://wiki.gnome.org/Apps/Web) (Lightweight browser), [Gedit](https://wiki.gnome.org/Apps/Gedit) (Text editor), [XFCE Terminal](https://docs.xfce.org/apps/terminal/start).
*   **Synchronization:** [Syncthing](https://syncthing.net/) (sharing files between devices without need for cloud or Internet).
*   **Language:** 🌐 **Multilingual.** All applications are installed with the selected local language support.

### 6. Hardware Support
*   **Standard PC:** Optimized for x86_64 architectures (Intel/AMD) through AppImages and Flatpaks.
*   **Raspberry Pi:** 🍓 **Official Support.** The installer automatically detects Raspberry Pi devices and uses native ARM packages to guarantee performance.

---

## 🔮 Roadmap (Future Planned Modules)

We are working to integrate these powerful tools in upcoming versions:

### 1. Automated Ingestion into Personal Vault
*   Improve scripts to automate data import into personalized vaults from multiple sources: Other USB devices, local hard drives, etc.

### 2. Education and Learning
*   **[Khan Academy Offline](https://en.khanacademy.org/):** Download of interactive math, science, and economics lessons for all ages.
*   **[Kolibri](https://learningequality.org/kolibri/) Platform:** A complete educational library with videos and exercises for schools in remote areas.

### 3. Literature and Technical Libraries
*   **[Project Gutenberg](https://www.gutenberg.org/):** Access to more than 70,000 classic public domain books.
*   **[Survivor Library](http://www.survivorlibrary.com/):** Massive collection of manuals on pre-industrial techniques (agriculture, forge, basic chemistry).
*   **[Other Libraries for Kiwix](https://download.kiwix.org/zim/):** Dictionaries, physics, mathematics, education, travel, etc.

### 4. Advanced Analysis with IA
*   **[AnythingLLM](https://useanything.com/) for PDF Analysis:** Tool to "chat" with your own local PDF documents.
*   **Model Expansion:** Increase the catalog of available models (Vision, Coding) according to hardware capabilities.

### 5. Networks and Communication
*   **SDR (Software Defined Radio):** Integration of tools like [Gqrx](https://gqrx.dk/) to receive news or data via radio in emergency situations.

### 6. Leisure and Entertainment
*   **Emulators:** Retro systems with a selection of free games.
*   **Games:** Selection of open-source indie games.

### 7. ❗ Technical Improvements
*   **Automatic Updater:** System for updating components and databases incrementally (although currently the installer can be launched as many times as necessary).
*   **Pregenerated Images:** Distribution of ready-to-use disk images in different languages for instant deployment.
*   **Hardware IA Acceleration:** GPU/NPU optimization for local AI models.
*   **More Hardware Support:** Expand hardware support to include more devices and architectures, including devices that the user may own and need to use in emergency situations (communication systems, wearables, etc.).
*   **Internacionalization:** Translation of the installer and documentation to more languages.