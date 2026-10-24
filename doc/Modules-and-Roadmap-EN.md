# Applications, Included Content, and Development Roadmap

refugiOS includes a selection of tools designed to work entirely without an Internet connection. Below are the modules currently available and those we plan to add soon.

> [!IMPORTANT]
> **Internationalization (i18n):** The installer, the launchers and the documentation are available in **Spanish and English**. More languages will follow depending on community interest.
>
> **Documentation Migration:** We are in the process of migrating all technical and user documentation to the **GitHub Wiki** format to facilitate consultation and collaboration.

---

## 🚀 Current Modules (Already Available)

These components are installed automatically or through the welcome wizard:

### 1. Offline Library and Encyclopedias ([Kiwix](https://www.kiwix.org/))
Access to massive databases using the ZIM format.
*   **Wikipedia in five tiers:** Lite (top articles, summarised), Essentials (top articles in full, no images), Essentials with images, NoPics (all articles, no images) and **Total with images and multimedia**. In English they take ~290 MB, ~2.6 GB, ~6.5 GB, ~49 GB and ~119 GB; the Spanish ones are much smaller (~34 GB the complete one). The installer preselects the largest one that comfortably fits on your drive.
*   **Library by category:** Besides Wikipedia, the installer offers a library organised in four menus, with freely available content published by Kiwix:
    *   **Health and medicine:** [WikiMed](https://www.kiwix.org/) (Wikipedia's medical articles), [WikEM](https://wikem.org/) (emergency medicine) and first aid and field medicine manuals.
    *   **Emergencies and survival:** Post-disaster guides, drinking water, food preparation, knots, Q&A on outdoor survival and [WikiHow](https://wikihow.com/).
    *   **Practical knowledge and repairs:** [iFixit](https://www.ifixit.com/), [Appropedia](https://www.appropedia.org/) (appropriate technology), [Energypedia](https://energypedia.info/) (solar and off-grid energy), gardening, home repairs, vehicle mechanics and amateur radio.
    *   **Language, books and education:** [Wiktionary](https://en.wiktionary.org/) (dictionary), [Wikivoyage](https://en.wikivoyage.org/) (with phrasebooks for other languages), Wikibooks, Wikisource and the [PhET](https://phet.colorado.edu/) science simulations.
*   **Desktop launchers:** Wikipedia, WikiMed and WikiHow get their own desktop icon; the other books are gathered in the **refugiOS Library** folder on the desktop, so it does not fill up with icons.
*   **Verified downloads:** Every file is downloaded through the Kiwix *metalink*, which spreads the download over several mirrors and checks every piece; if that fails, each mirror is tried directly and finally BitTorrent. The result is checked against the published SHA-256, and an interrupted download is never taken as installed: running the installer again resumes it.
*   **Language:** 🌐 **Multilingual.** The installer downloads the files in the language you choose and falls back to English when a book does not exist in it. Books that only exist in English are marked as such in the menu.

### 2. Maps and Navigation ([Organic Maps](https://organicmaps.app/))
Detailed vector maps with offline search and routing.
*   **Contents:** Maps of cities, trails, water sources, and hospitals.
*   **Maps ready from the installer:** The installer itself offers common regions (Spain, Portugal, the whole of Europe, Mexico, Colombia, Argentina, Chile, Peru, Venezuela, Brazil or the United States), downloaded and verified straight into the Organic Maps folder. Any other region can be downloaded later from the application itself, while there is a connection.
*   **Language:** 🌐 **Multilingual.** The interface and map names adapt to your region.

### 3. Artificial Intelligence Assistant ([Llamafile](https://github.com/Mozilla-Ocho/llamafile))
Private smart assistant that works 100% on your local computer. Available in five levels according to device capacity:
*   ⚪ **Minimal:** [Qwen3-0.6B](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) (0.6B, Q4_K_M) — ~380 MB. For devices with limited resources (min. 4 GB RAM).
*   🟢 **Basic:** [Gemma-4-E4B-it](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF) (4B, Q4_K_M) — ~4.7 GB. For PCs with 8 GB of RAM.
*   🟡 **Intermediate:** [Qwen3-8B](https://huggingface.co/unsloth/Qwen3-8B-GGUF) (8B, Q4_K_M) — ~4.8 GB. For modern laptops with 8 GB of RAM.
*   🔴 **Advanced:** [Qwen3-14B](https://huggingface.co/unsloth/Qwen3-14B-GGUF) (14B, Q4_K_M) — ~8.6 GB. For powerful PCs with 16 GB of RAM.
*   ⚫ **Ultra:** [Gemma-4-26B-A4B-it](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) (26B MoE, Q4_K_M) — ~16.2 GB. For workstations with 32 GB of RAM.
*   **Smart Selector:** When launching the assistant, a script detects total RAM and GPU VRAM (NVIDIA/AMD), reserves a strict 2 GB safety margin for the OS (prevents USB swap), and shows an interactive menu with only installed models, automatically preselecting the most powerful one the hardware can run.
*   **Emergency context:** The chat interface starts with a system message in your language asking for clear, short and practical answers, putting urgent steps first in medical or safety matters and reminding that the assistant has no Internet access.
*   **Language:** 🌐 **Multilingual.** All models understand and respond in more than 20 languages.

### 4. Cryptographic Vaults (LUKS)
Secure and encrypted storage system for sensitive data.
*   **Status:** Unified interactive manager with a single desktop icon and dialog-based menus.
*   **Features:** Support for multiple simultaneous vaults with status display (open/closed), custom names, variable sizes, creation, opening, closing, and permanent deletion.
*   **Automation:** Intelligent USB drive detection for size suggestions and automated data import.


### 5. Offline Translator ([LocalTranslate](https://terslang.github.io/LocalTranslate/))
*   **Contents:** Translation of texts between more than 40 languages with Firefox's neural translation models, bundled inside the application: nothing else needs downloading.
*   **Installation:** Optional from the installer (~2.7 GB, plus ~1.6 GB of components shared with Organic Maps if that is not installed). Creates the **Translator** desktop icon.
*   **Companions:** The Wikivoyage phrasebooks and Wiktionary (in the library) help with pronunciation and vocabulary.

### 6. Check my refugiOS
*   **What it does:** A desktop icon checks, without any connection, that everything installed is complete and intact: interrupted downloads, damaged files, broken shortcuts, AI models that do not fit in the computer's memory, missing maps and damaged vaults. It ends with a report, also saved to `~/refugiOS/check-report.txt`.
*   **Two modes:** The quick check takes a few seconds; the full check also recomputes the checksum of every file and can take a while on a slow drive.
*   **When to use it:** After the installation, before putting the device away, and after cloning it to another drive.

### 6b. Update refugiOS
*   **What it does:** A desktop icon looks, while online, for new editions of the installed books (or the book in your language if you had the English one), new versions of Kiwix, the AI engine and the applications, new revisions of the AI models, and newer map data for the regions you already had. It shows the list with the size of each item and applies the ones you choose.
*   **No risk:** Every new version is downloaded next to the old one and verified against its published checksum; only then is the old one removed. If an update fails or is interrupted, the device stays exactly as it was and keeps working offline. Updates that do not fit in the free space are skipped.
*   **When to use it:** Now and then, while there is a connection. refugiOS never needs it to keep working.

### 7. Standard Work Tools
Essential programs for daily life, adapted for maximum compatibility.
*   **Office and Multimedia:** [LibreOffice](https://www.libreoffice.org/), [VLC](https://www.videolan.org/), [Evince](https://wiki.gnome.org/Apps/Evince) (PDF).
*   **System and Navigation:** [Epiphany Browser](https://wiki.gnome.org/Apps/Web) (Lightweight browser), [Gedit](https://wiki.gnome.org/Apps/Gedit) (Text editor), [XFCE Terminal](https://docs.xfce.org/apps/terminal/start).
*   **Synchronization:** [Syncthing](https://syncthing.net/) (sharing files between devices without need for cloud or Internet).
*   **Spelling:** The spelling, hyphenation and thesaurus dictionaries of the chosen language are installed, used by LibreOffice and the text editor.
*   **Language:** 🌐 **Multilingual.** All applications are installed with the selected local language support.

### 8. Hardware Support
*   **Standard PC:** Optimized for x86_64 architectures (Intel/AMD) through AppImages and Flatpaks.
*   **Raspberry Pi:** 🍓 **Official Support.** The installer automatically detects Raspberry Pi devices and uses native ARM packages to guarantee performance.

---

## 🔮 Roadmap (Future Planned Modules)

We are working to integrate these powerful tools in upcoming versions:



### 2. Education and Learning
*   **[Khan Academy Offline](https://en.khanacademy.org/):** Download of interactive math, science, and economics lessons for all ages.
*   **[Kolibri](https://learningequality.org/kolibri/) Platform:** A complete educational library with videos and exercises for schools in remote areas.

### 3. Literature and Technical Libraries
*   **[Project Gutenberg](https://www.gutenberg.org/):** ✅ **Now available** in Spanish. The complete English collection is over 200 GB and is pending to be offered by subject.
*   **[Survivor Library](http://www.survivorlibrary.com/):** Massive collection of manuals on pre-industrial techniques (agriculture, forge, basic chemistry).
*   **[Other Libraries for Kiwix](https://download.kiwix.org/zim/):** ✅ **Now available:** dictionary, travel guides, textbooks, repairs, energy and survival (see above). More will be added.

### 4. Advanced Analysis with IA
*   **[AnythingLLM](https://useanything.com/) for PDF Analysis:** Tool to "chat" with your own local PDF documents.
*   **Model Expansion:** Increase the catalog of available models (Vision, Coding) according to hardware capabilities.

### 5. Networks and Communication
*   **SDR (Software Defined Radio):** Integration of tools like [Gqrx](https://gqrx.dk/) to receive news or data via radio in emergency situations.

### 6. Leisure and Entertainment
*   **Emulators:** Retro systems with a selection of free games.
*   **Games:** Selection of open-source indie games.

### 7. ❗ Technical Improvements
*   **Updater:** ✅ **Now available** (*Update refugiOS* icon, see above). Pending: Notify automatically that updates exist when the computer is online.
*   **Pre-generated Images:** ✅ **Now available.** Distribution of ready-to-use disk images in different languages for instant deployment from [refugios.ganso.org](https://refugios.ganso.org/).
*   **Hardware IA Acceleration:** GPU/NPU optimization for local AI models.
*   **More Hardware Support:** Expand hardware support to include more devices and architectures, including devices that the user may own and need to use in emergency situations (communication systems, wearables, etc.).
*   **Internacionalization:** Translation of the installer and documentation to more languages.