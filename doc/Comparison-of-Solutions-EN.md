# Comparison: Why refugiOS?

Several solutions exist designed to store information and useful tools in case of emergency. However, many of them have technical limitations that refugiOS tries to resolve.

---

## 1. Other Solutions in the Market

### Project N.O.M.A.D.
It is a very complete and visually attractive platform that includes Wikipedia, medical tools, and Artificial Intelligence.
*   **Limitation:** It works via "containers" (Docker). This means you need a computer with an operating system already installed and working perfectly to use it. If your computer's hard drive breaks, you won't be able to access the information. Furthermore, it requires a very powerful processor and a lot of RAM.

### Internet-in-a-Box (IIAB)
It is the reference project for bringing school libraries to remote areas without Internet.
*   **Limitation:** It is designed primarily to work on small devices like Raspberry Pi and act as a Wi-Fi router that others connect to. It is not intended to be used as a full desktop operating system on any computer.

### Prepper Disk / Survival SSD
These are USB units or SSD disks that are sold already configured with thousands of manuals and survival guides.
*   **Limitation:** Often they are just file "warehouses." If the computer where you connect them does not have the proper programs to open those files (such as map or ZIM encyclopedia readers), the disk is useless. Furthermore, they usually have very high prices.

---

## 2. Other Bootable Linux Distros

### Tails (The Amnesic Incognito Live System)

It is the reference system for extreme privacy and anonymity on the net.
*   **Limitation:** It is designed to "leave no trace" (it's amnesic), which makes it difficult to save vital documents permanently without a complex configuration. It lacks by default the offline survival library and local AI that refugiOS allows to integrate.

### Ultralight Distros (Puppy Linux / AntiX)

Famous for reviving old hardware due to their low resource consumption.
*   **Limitation:** They are delivered as a blank canvas. A user in an emergency would have to spend hours manually configuring maps, readers, and AI models. Also, they may have more limited hardware support and are not adaptable to systems like Raspberry OS. In general, they are perfect for a user with knowledge and time to analyze and integrate the available modules, especially if you have a limited spectrum of devices where you plan to use it, but they are not for most users.

---

## 3. The Advantages of refugiOS

refugiOS has been designed to overcome these obstacles following a **"boot and go"** philosophy.

### How is it different?

1.  **Integral System Transformation:**
It's not just a USB with files. refugiOS is a tool that personalizes systems like Xubuntu or Raspberry Pi OS so that they work independently and optimized from a pendrive.

2.  **"Ready for Disaster" Environment:**
All tools (map readers, encyclopedias, artificial intelligence) are installed and configured by the script. You don't have to install anything manually on the final system.

3.  **Maximum Performance on Modest Devices:**
By optimizing the base operating system directly (like Xubuntu), refugiOS takes full advantage of hardware power without intermediate layers like Docker. This allows AI and maps to work fast even on old laptops.

4.  **Security and Persistence:**
It implements professional encryption tools (LUKS) to protect your personal documents, allowing critical information to survive reboots securely.

5.  **Free, Open, and Auditable:**
It's an open-source project. Anyone can audit the customization scripts, see what changes are made, and create their own emergency device without depending on third parties.
