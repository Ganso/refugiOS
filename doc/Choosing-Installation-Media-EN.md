# Choosing Installation Media

Before installing refugiOS —whether via a Xubuntu Live ISO, a native system image, or any other method— you need to choose the **physical device** it will run on. This guide is common to all installation methods and will help you make the best decision based on your budget and needs.

> [!NOTE]
> If you are installing refugiOS on a **Raspberry Pi**, the installation media is different (microSD card or SSD via HAT/USB). See the **[Raspberry Pi Installation Guide](Raspberry-Pi-Installation-EN.md#1-necessary-hardware)** for platform-specific details.

---

## 1. Device Type: Pendrive vs SSD

The most important difference is not the capacity, but the **type of memory**:

*   **Golden Recommendation:** Although a standard pendrive works, the ideal for good performance is a **pocket SSD drive** (or a USB adapter for M.2 NVMe drives). Cheap USB sticks wear out quickly under constant Linux use and their writing speed is very poor.
*   **Pendrive (USB Memory):** It's the size of a thumb, very light and cheap. It gets very hot and its speed drops drastically after 5 minutes of use.
*   **Pocket SSD:** It's somewhat larger (like a lighter or a matchbox), usually has a metal case and speeds that don't drop below 400 MB/s. It's a real disk drive, but miniaturized.

> [!WARNING]
> The **Native Installation** method (both in Xubuntu ISO and system image) is not recommended on conventional pendrives because Linux "journaling" will destroy them in a few months. **Use it only if you have an SSD via USB.** Live mode with persistence is safer for standard pendrives.

---

## 2. Capacity and Content

The device size determines what content you can store:

| Capacity | Possible Content | Use Profile |
| :--- | :--- | :--- |
| **16 GB (Minimum)** | Base system + WikiMed + Basic Maps + Light AI. No space for Wikipedia. | Basic emergency unit |
| **32 GB (Balanced)** | All of the above + Wikipedia without images. No room for full Wikipedia. | Functional backup |
| **64 GB (Standard)** | Full Wikipedia with images + Phi-4-mini AI + WikiMed + Maps. Limited room for more. | Recommended daily use |
| **128 GB or more** | All the above + WikiHow + multiple AI models + detailed world maps. | Advanced station |

---

## 3. Buying Tips

### What to look for

*   **USB Version:** Always look for **USB 3.0, 3.1, or 3.2** (sometimes marked as "Gen 1" or "Gen 2"). The connector is usually blue or red inside.
*   **Speed:** On the box, look for read speeds above **150 MB/s** and write speeds above **50 MB/s**.
*   **Format:** Those with metal casings dissipate heat better during intensive use.

### What to avoid

*   **USB 2.0:** It is desperately slow to run an operating system. A boot that takes 30 seconds on USB 3.0 can take 10 minutes on USB 2.0.
*   **Unknown Brands:** Flee from "too good to be true" offers of 1 TB for €10; they are usually scams with tiny real capacity.

### What to ask for in the store (or search on Amazon)

If you go to a physical store or search online, use these magic words not to fail:

*   **In physical store:** *"I want an external pocket SSD drive, that is USB 3.2 and at least 64GB (or 128GB), with read speed above 400 MB/s"*.
*   **In online stores:** Search for *"Portable SSD 128GB USB 3.2"* or *"External solid state unit USB-C"*. Make sure the description says **"SSD"** and not just "Flash Drive" or "USB Stick".

### Backup Strategy

If you have old or smaller pendrives (16 GB), don't throw them away. You can leave them as **backup units** in a backpack, first aid kit, or vehicle with the base system. Always carry "the good one" (fast SSD or USB 3.2) as your main unit.

---

## 4. Reference Options and Budgets (Spain)

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

### Performance and Experience Comparison (2026)

| Use Profile | Capacity | Investment (Est.) | Installation Time | User Experience |
| :--- | :--- | :--- | :--- | :--- |
| **OS Distribution** | 32 GB - 64 GB | 10 € - 20 € | A full afternoon | With continuous waits |
| **SSD Recycling** | 128 GB - 256 GB | 15 € (Adap. only) | ~1 hour | Fluid (almost native) |
| **High Performance** | 250 GB | 60 € - 90 € | < 45 minutes | Responsive (like local) |

> [!IMPORTANT]
> This price ecosystem reflects that the 2026 market penalizes lower capacities. The price difference between a slow pendrive and a 250GB SSD is today one of the most important value gaps for the end user.

---

## 5. Implications by Installation Method

The type of device you choose also influences which installation method suits you best:

| Installation Method | USB 3.x Pendrive | USB SSD | SATA Adapter |
| :--- | :--- | :--- | :--- |
| **Live ISO with Persistence** | ✅ Recommended for pendrives | ✅ Functional | ✅ Functional |
| **Native System Image** | ⚠️ Possible but fast wear | ✅ Recommended for SSD | ✅ Recommended for SSD |
| **Native XUbuntu Installation** | ❌ Not recommended (journaling) | ✅ SSD only | ✅ SSD only |

> [!TIP]
> If you have a **standard pendrive**, use the Live ISO with Persistence method (Xubuntu). If you have an **SSD**, you can choose any method; the native system image offers the best performance and least wear.

---

[Back to documentation](../README.md)
