# refugiOS Unit Cloning Guide

If you have already configured your first **refugiOS** pendrive and want to make an exact copy for a relative, a friend, or simply to have a backup, this guide explains how to clone it step by step.

## 1. Cloning in Windows

To clone a pendrive in Windows, the simplest and most reliable tool is **HDD Raw Copy Tool**.

1.  Download and install [HDD Raw Copy Tool](https://hddguru.com/software/HDD-Raw-Copy-Tool/) (there is a portable version that does not require installation).
2.  Connect your refugiOS pendrive (Source) and the new pendrive (Target).
3.  Open the program:
    *   **SOURCE:** Select your current refugiOS pendrive. Click *Continue*.
    *   **TARGET:** Select the new pendrive where you want to dump the copy. **Warning! Everything on it will be erased.** Click *Continue*.
4.  Click **START** and wait for the process to finish.

## 2. Cloning in Ubuntu and Derivatives (Linux)

In Linux, you have two options: a graphical one and another via terminal.

### Option A: Disk Utility (Graphical)
This is the safest way to avoid errors when typing device names.

1.  Find and open the **Disks** application (gnome-disks).
2.  Select your refugiOS pendrive in the left column.
3.  Click on the three-dot menu (top right) and choose **Create disk image...**. Save it on your computer.
4.  Once created, disconnect the original pendrive and connect the new one.
5.  Select the new pendrive in the list, click the three dots again, and choose **Restore disk image...**. Select the file you just created.

### Option B: Terminal (`dd` command)
This is the fastest method but **requires great caution**. An error in the drive letters can erase your main hard drive.

1.  Identify your units with `lsblk`. Suppose `/dev/sdb` is the source and `/dev/sdc` is the destination.
2.  Run the command to copy bit by bit:
    ```bash
    sudo dd if=/dev/sdb of=/dev/sdc bs=64K conv=noerror,sync status=progress
    ```

---

## 3. What if the Sizes are Different?

It's very common for two pendrives that claim to be "64GB" to actually have a few megabytes of difference.

### Case A: The Target is LARGER than the Source
The cloning process will work perfectly, but you will see that on the new pendrive there is "leftover" space at the end that you cannot use.
*   **Solution:** Open the **GParted** tool in Linux or **Disk Management** in Windows and expand the last partition (`writable` or the data one) to occupy all the remaining space.

### Case B: The Target is SMALLER than the Source
Even if it's only by one MB, the cloning will fail or leave a corrupt unit at the end.
*   **Solution:** Before cloning, you must **reduce the size of the last partition** of the original pendrive.
    1. Use **GParted** to shrink the data partition of the source so that the total size of the partitions is smaller than the capacity of the target pendrive.
    2. Perform the cloning normally.
    3. Once cloned, you can expand the partition again on both pendrives if you wish.

---

> [!TIP]
> **Resilience Tip:**
> Having a physical backup is vital. If your main pendrive is lost or physically damaged by prolonged use, having a clone already configured will save you hours of downloading and installation in an emergency situation.
