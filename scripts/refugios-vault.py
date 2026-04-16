#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
refugiOS - Secure Vault Manager (Python)
Unified script for creating, opening, and closing encrypted LUKS vaults.

Usage: python3 refugios-vault.py <create|open|close>

Dependencies: python3-dialog (installed by install.sh), i18n.py (project module)
All other imports are Python standard library.
"""

import os
import sys
import subprocess
import shutil
import re
import json
import glob
import math

# Localization system
try:
    import i18n
except ImportError:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    try:
        import i18n
    except ImportError:
        print("\033[1;31m[X] ERROR:\033[0m Could not find 'i18n.py'.")
        sys.exit(1)

try:
    import dialog
except ImportError:
    print(i18n.T('dialog_error'))
    sys.exit(1)

# ==============================================================================
# CONSTANTS
# ==============================================================================

HOME_DIR = os.environ['HOME']
BASE_DIR = os.path.join(HOME_DIR, "refugiOS")
VAULT_DIR = os.path.join(BASE_DIR, "Vaults")
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")

# Detect desktop directory
DESKTOP_DIR = os.path.join(HOME_DIR, "Desktop")
if not os.path.isdir(DESKTOP_DIR):
    DESKTOP_DIR = os.path.join(HOME_DIR, "Escritorio")

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def log_info(msg):
    """Displays an informative message in blue."""
    print(f"\033[1;34m[*]\033[0m {msg}")

def log_err(msg):
    """Displays an error message in red."""
    print(f"\033[1;31m[X] {i18n.T('error')}:\033[0m {msg}")

def log_success(msg):
    """Displays a success message in green."""
    print(f"\033[1;32m[v] {i18n.T('success')}:\033[0m {msg}")

def run_cmd(cmd, shell=True, check=True, quiet=False):
    """
    Executes a command in the system terminal.
    :return: True if command succeeded, False otherwise.
    """
    try:
        stdout = subprocess.DEVNULL if quiet else None
        stderr = subprocess.DEVNULL if quiet else None
        subprocess.run(cmd, shell=shell, check=check, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError:
        return False
    return True

def get_cmd_output(cmd):
    """Executes a command and returns its stdout output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return result.stdout.strip()
    except Exception:
        return ""

def init_dialog():
    """Initializes a pythondialog Dialog instance with color support."""
    d = dialog.Dialog(autowidgetsize=True)
    try:
        d.add_persistent_args(["--colors"])
    except AttributeError:
        pass
    return d

def get_mapper_name(vault_name):
    """Returns the /dev/mapper name for a vault."""
    return f"vault_{vault_name}"

def get_mount_point(vault_name):
    """Returns the mount point directory for a vault."""
    icon_name = i18n.T('vault_mount_prefix')
    return os.path.join(DESKTOP_DIR, f"{icon_name}_{vault_name}")

def get_desktop_file(vault_name):
    """Returns the .desktop file path for an open vault icon."""
    return os.path.join(DESKTOP_DIR, f"Vault_{vault_name}.desktop")

# ==============================================================================
# VAULT DISCOVERY
# ==============================================================================

def list_all_vaults():
    """
    Scans the Vaults directory for .img files.
    Returns a list of vault names (without path or extension).
    """
    if not os.path.isdir(VAULT_DIR):
        return []
    vaults = []
    for f in sorted(os.listdir(VAULT_DIR)):
        if f.endswith('.img'):
            vaults.append(f[:-4])  # Remove .img extension
    return vaults

def list_open_vaults():
    """
    Detects which vaults are currently open by checking /dev/mapper/vault_*.
    Returns a list of vault names that are currently open.
    """
    open_vaults = []
    mapper_path = "/dev/mapper"
    if os.path.isdir(mapper_path):
        for entry in os.listdir(mapper_path):
            if entry.startswith("vault_"):
                vault_name = entry[6:]  # Remove 'vault_' prefix
                open_vaults.append(vault_name)
    return open_vaults

# ==============================================================================
# USB DETECTION
# ==============================================================================

def detect_usb_drives():
    """
    Detects mounted USB drives using lsblk.
    Returns a list of dicts with: device, mountpoint, size_mb, used_mb
    """
    usb_drives = []
    try:
        # Get list of removable block devices
        output = get_cmd_output(
            "lsblk -J -o NAME,MOUNTPOINT,SIZE,FSUSED,HOTPLUG,TYPE,TRAN 2>/dev/null"
        )
        if not output:
            return usb_drives


        data = json.loads(output)

        for device in data.get('blockdevices', []):
            # Check if this is a USB device (hotplug or usb transport)
            is_usb = (device.get('tran') == 'usb' or device.get('hotplug') == '1'
                      or device.get('hotplug') is True)
            if not is_usb:
                continue

            # Check partitions (children) of the USB device
            children = device.get('children', [])
            if not children:
                # Device itself might be mounted (no partition table)
                children = [device]

            for part in children:
                mountpoint = part.get('mountpoint')
                if not mountpoint or mountpoint in ['/', '/boot', '/boot/efi']:
                    continue

                # Calculate used space
                try:
                    usage = shutil.disk_usage(mountpoint)
                    used_bytes = usage.total - usage.free
                    used_mb = math.ceil(used_bytes / (1024 * 1024)) if used_bytes > 0 else 0
                    total_mb = usage.total // (1024 * 1024)
                except Exception:
                    continue

                usb_drives.append({
                    'device': f"/dev/{part.get('name', '?')}",
                    'mountpoint': mountpoint,
                    'total_mb': total_mb,
                    'used_mb': used_mb
                })

    except Exception:
        pass

    return usb_drives

def check_root_free_space(required_mb):
    """
    Checks if creating a vault of 'required_mb' MB would leave at least
    10% of the current free space as a safety buffer on the root filesystem.
    Returns (ok, max_recommended_mb).
    """
    try:
        usage = shutil.disk_usage('/')
        free_mb = usage.free // (1024 * 1024)
        # Reserve 10% of current free space as safety buffer
        safety_buffer = free_mb * 10 // 100
        max_allowed = free_mb - safety_buffer

        if required_mb <= max_allowed:
            return True, max_allowed
        else:
            return False, max(0, max_allowed)
    except Exception:
        return True, 0

# ==============================================================================
# DESKTOP ICON MANAGEMENT
# ==============================================================================

def create_vault_desktop_icon(vault_name, mount_point):
    """Creates a .desktop file on the desktop for accessing an open vault."""
    desktop_file = get_desktop_file(vault_name)
    display_name = f"{i18n.T('vault_icon_label')}: {vault_name}"

    with open(desktop_file, 'w') as f:
        f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={display_name}
Comment={i18n.T('vault_icon_comment')}
Exec=xdg-open "{mount_point}"
Icon=folder-locked
Terminal=false
""")
    os.chmod(desktop_file, 0o755)

    # Mark as trusted for XFCE/GNOME
    if shutil.which("gio"):
        run_cmd(f"gio set '{desktop_file}' metadata::trusted yes", quiet=True)
        checksum = get_cmd_output(f"sha256sum '{desktop_file}' | awk '{{print $1}}'")
        if checksum:
            run_cmd(f"gio set '{desktop_file}' metadata::xfce-exe-checksum '{checksum}'", quiet=True)

def remove_vault_desktop_icon(vault_name):
    """Removes the .desktop icon for a vault from the desktop."""
    desktop_file = get_desktop_file(vault_name)
    if os.path.exists(desktop_file):
        os.remove(desktop_file)

# ==============================================================================
# OPERATION: CREATE VAULT
# ==============================================================================

def op_create(d):
    """Handles the vault creation flow with Dialog UI."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    existing = list_all_vaults()

    # Step 1: Ask for vault name
    while True:
        code, name = d.inputbox(
            i18n.T('vault_name_prompt'),
            title=i18n.T('vault_create_title'),
            init=i18n.T('vault_default_name')
        )
        if code != d.OK:
            return

        name = name.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            d.msgbox(i18n.T('vault_name_invalid'), title=i18n.T('error'))
            continue

        if name in existing or os.path.exists(os.path.join(VAULT_DIR, f"{name}.img")):
            d.msgbox(i18n.T('vault_name_exists'), title=i18n.T('error'))
            continue

        break

    # Step 2: Detect USB drives
    usb_drives = detect_usb_drives()
    selected_usb = None
    suggested_size = 3072  # Default 3 GB

    if usb_drives:
        # Use the first USB drive found
        usb = usb_drives[0]
        selected_usb = usb
        base_suggested = int(usb['used_mb'] * 1.5)
        usb_suggested = max(100, base_suggested)

        # Check root filesystem space
        space_ok, max_allowed = check_root_free_space(usb_suggested)

        if space_ok:
            suggested_size = usb_suggested
            usb_info = i18n.T('vault_usb_detected').format(
                usb['device'], usb['used_mb'], suggested_size
            )
        else:
            # Reduce suggestion to fit
            if max_allowed > 0:
                suggested_size = max_allowed
            else:
                suggested_size = 0
                
            usb_info = i18n.T('vault_usb_detected').format(
                usb['device'], usb['used_mb'], base_suggested
            )
            usb_info += "\n\n" + i18n.T('vault_usb_no_space').format(
                usb_suggested, max_allowed
            )

        d.msgbox(usb_info, title=i18n.T('vault_create_title'))

    # Step 3: Ask for vault size
    size_hint = i18n.T('vault_size_recommendation')
    while True:
        code, size_str = d.inputbox(
            f"{i18n.T('vault_size_prompt')}\n\n{size_hint}",
            title=i18n.T('vault_create_title'),
            init=str(suggested_size)
        )
        if code != d.OK:
            return

        try:
            size_mb = int(size_str.strip())
            if size_mb < 10:
                raise ValueError
        except ValueError:
            d.msgbox(i18n.T('vault_size_invalid'), title=i18n.T('error'))
            continue

        # Verify root filesystem space
        space_ok, max_allowed = check_root_free_space(size_mb)
        if not space_ok:
            d.msgbox(
                i18n.T('vault_usb_no_space').format(size_mb, max_allowed),
                title=i18n.T('warning')
            )
            continue

        break

    # Step 4: Confirm creation
    confirm_msg = i18n.T('vault_confirm_create').format(name, size_mb)
    if d.yesno(confirm_msg, title=i18n.T('vault_create_title'),
               yes_label=i18n.T('yes'), no_label=i18n.T('no')) != d.OK:
        return

    # Step 5: Create the vault
    vault_file = os.path.join(VAULT_DIR, f"{name}.img")
    mapper = get_mapper_name(name)

    log_info(i18n.T('vault_creating'))
    print()  # Visual separation before dd output

    # Fill with random data
    if not run_cmd(f"dd if=/dev/urandom of=\"{vault_file}\" bs=1M count={size_mb} status=progress"):
        d.msgbox(i18n.T('vault_error_create'), title=i18n.T('error'))
        return

    # LUKS format (interactive - asks for password via terminal)
    # --batch-mode skips the redundant "Are you sure?" prompt since we already confirmed via Dialog
    print(f"\n\033[1;33m{i18n.T('vault_set_password')}\033[0m")
    print(f"\033[1;31m{i18n.T('vault_password_warning')}\033[0m\n")
    if not run_cmd(f"sudo cryptsetup luksFormat --batch-mode \"{vault_file}\""):
        # Cleanup on failure
        os.remove(vault_file)
        d.msgbox(i18n.T('vault_error_create'), title=i18n.T('error'))
        return

    # Format internal filesystem
    if not run_cmd(f"sudo cryptsetup open \"{vault_file}\" {mapper}"):
        os.remove(vault_file)
        d.msgbox(i18n.T('vault_error_create'), title=i18n.T('error'))
        return

    run_cmd(f"sudo mkfs.ext4 /dev/mapper/{mapper}", quiet=True)
    run_cmd(f"sudo cryptsetup close {mapper}", quiet=True)

    log_success(i18n.T('vault_created_ok').format(name))

    # Step 6: Offer USB data import if conditions are met
    if selected_usb and size_mb >= selected_usb['used_mb']:
        if d.yesno(i18n.T('vault_import_usb_prompt'),
                   title=i18n.T('vault_create_title'),
                   yes_label=i18n.T('yes'), no_label=i18n.T('no')) == d.OK:
            _import_usb_to_vault(d, name, vault_file, selected_usb)

    d.msgbox(i18n.T('vault_created_ok').format(name), title=i18n.T('success'))

def _import_usb_to_vault(d, vault_name, vault_file, usb_info):
    """Opens a newly created vault, imports USB data via rsync, then closes it."""
    mapper = get_mapper_name(vault_name)
    mount_point = get_mount_point(vault_name)

    log_info(i18n.T('vault_importing'))

    # Open vault for import (will ask password via terminal)
    print(f"\n\033[1;33m{i18n.T('vault_enter_password')}\033[0m\n")
    if not run_cmd(f"sudo cryptsetup open \"{vault_file}\" {mapper}"):
        d.msgbox(i18n.T('vault_error_open'), title=i18n.T('error'))
        return

    os.makedirs(mount_point, exist_ok=True)
    if not run_cmd(f"sudo mount /dev/mapper/{mapper} \"{mount_point}\""):
        run_cmd(f"sudo cryptsetup close {mapper}", quiet=True)
        d.msgbox(i18n.T('vault_error_open'), title=i18n.T('error'))
        return

    run_cmd(f"sudo chown -R $USER:$USER \"{mount_point}\"", quiet=True)

    # Copy data from USB to vault
    usb_mount = usb_info['mountpoint']
    success = run_cmd(f"rsync -av --progress \"{usb_mount}/\" \"{mount_point}/\"")

    # Close vault after import
    run_cmd(f"sudo umount \"{mount_point}\"", quiet=True)
    run_cmd(f"sudo cryptsetup close {mapper}", quiet=True)
    if os.path.isdir(mount_point):
        try:
            os.rmdir(mount_point)
        except OSError:
            pass

    if success:
        log_success(i18n.T('vault_import_ok'))
        d.msgbox(i18n.T('vault_import_ok'), title=i18n.T('success'))
    else:
        d.msgbox(i18n.T('vault_error_import'), title=i18n.T('error'))

# ==============================================================================
# OPERATION: OPEN VAULT
# ==============================================================================

def op_open(d):
    """Handles the vault opening flow with Dialog UI."""
    all_vaults = list_all_vaults()
    open_vaults = list_open_vaults()

    if not all_vaults:
        d.msgbox(i18n.T('vault_none_found'), title=i18n.T('vault_open_title'))
        return

    # Filter out already open vaults
    available = [v for v in all_vaults if v not in open_vaults]
    if not available:
        already_names = ", ".join(open_vaults)
        d.msgbox(
            i18n.T('vault_all_already_open').format(already_names),
            title=i18n.T('vault_open_title')
        )
        return

    # Select vault to open
    if len(available) == 1:
        vault_name = available[0]
        if d.yesno(
            i18n.T('vault_confirm_open').format(vault_name),
            title=i18n.T('vault_open_title'),
            yes_label=i18n.T('yes'), no_label=i18n.T('no')
        ) != d.OK:
            return
    else:
        choices = [(v, f"{v}.img", False) for v in available]
        code, vault_name = d.radiolist(
            i18n.T('vault_select_open'),
            choices=choices,
            title=i18n.T('vault_open_title')
        )
        if code != d.OK or not vault_name:
            return

    # Open the vault
    vault_file = os.path.join(VAULT_DIR, f"{vault_name}.img")
    mapper = get_mapper_name(vault_name)
    mount_point = get_mount_point(vault_name)

    log_info(i18n.T('vault_open').format(vault_name))

    # cryptsetup open (password via terminal)
    print(f"\n\033[1;33m{i18n.T('vault_enter_password')}\033[0m\n")
    if not run_cmd(f"sudo cryptsetup open \"{vault_file}\" {mapper}"):
        d.msgbox(i18n.T('vault_error_open'), title=i18n.T('error'))
        return

    os.makedirs(mount_point, exist_ok=True)

    if not run_cmd(f"sudo mount /dev/mapper/{mapper} \"{mount_point}\""):
        run_cmd(f"sudo cryptsetup close {mapper}", quiet=True)
        d.msgbox(i18n.T('vault_error_open'), title=i18n.T('error'))
        return

    run_cmd(f"sudo chown -R $USER:$USER \"{mount_point}\"", quiet=True)

    # Create desktop icon
    create_vault_desktop_icon(vault_name, mount_point)

    log_success(i18n.T('vault_opened_ok').format(vault_name))

    # Inform user about the desktop icon
    d.msgbox(
        i18n.T('vault_opened_ok').format(vault_name) + "\n\n" +
        i18n.T('vault_desktop_icon_info'),
        title=i18n.T('vault_open_title')
    )

# ==============================================================================
# OPERATION: CLOSE VAULT
# ==============================================================================

def op_close(d):
    """Handles the vault closing flow with Dialog UI."""
    open_vaults = list_open_vaults()

    if not open_vaults:
        d.msgbox(i18n.T('vault_none_open'), title=i18n.T('vault_close_title'))
        return

    if len(open_vaults) == 1:
        vault_name = open_vaults[0]
        if d.yesno(
            i18n.T('vault_confirm_close').format(vault_name),
            title=i18n.T('vault_close_title'),
            yes_label=i18n.T('yes'), no_label=i18n.T('no')
        ) != d.OK:
            return
        _close_vault(vault_name)
        d.msgbox(i18n.T('vault_closed_ok').format(vault_name), title=i18n.T('success'))
    else:
        # Multiple open vaults: offer to select one or close all
        close_all_label = i18n.T('vault_close_all')
        choices = [("__ALL__", close_all_label, False)]
        for v in open_vaults:
            choices.append((v, f"{v}.img", False))

        code, selected = d.radiolist(
            i18n.T('vault_select_close'),
            choices=choices,
            title=i18n.T('vault_close_title')
        )
        if code != d.OK or not selected:
            return

        if selected == "__ALL__":
            for v in open_vaults:
                _close_vault(v)
            d.msgbox(i18n.T('vault_all_closed'), title=i18n.T('success'))
        else:
            if d.yesno(
                i18n.T('vault_confirm_close').format(selected),
                title=i18n.T('vault_close_title'),
                yes_label=i18n.T('yes'), no_label=i18n.T('no')
            ) != d.OK:
                return
            _close_vault(selected)
            d.msgbox(i18n.T('vault_closed_ok').format(selected), title=i18n.T('success'))

def _close_vault(vault_name):
    """Performs the actual vault closing: umount, cryptsetup close, cleanup."""
    mapper = get_mapper_name(vault_name)
    mount_point = get_mount_point(vault_name)

    log_info(i18n.T('vault_close').format(vault_name))

    # Unmount
    run_cmd(f"sudo umount \"{mount_point}\" 2>/dev/null", quiet=True)

    # Close LUKS
    run_cmd(f"sudo cryptsetup close {mapper} 2>/dev/null", quiet=True)

    # Remove mount point directory
    if os.path.isdir(mount_point):
        try:
            os.rmdir(mount_point)
        except OSError:
            pass

    # Remove desktop icon
    remove_vault_desktop_icon(vault_name)

    log_success(i18n.T('vault_closed_ok').format(vault_name))

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    if os.geteuid() == 0:
        log_err("This script should not be run as root. Run it as your regular user.")
        sys.exit(1)

    if len(sys.argv) < 2 or sys.argv[1] not in ('create', 'open', 'close'):
        print(f"Usage: {sys.argv[0]} <create|open|close>")
        sys.exit(1)

    operation = sys.argv[1]
    d = init_dialog()

    if operation == 'create':
        op_create(d)
    elif operation == 'open':
        op_open(d)
    elif operation == 'close':
        op_close(d)

if __name__ == "__main__":
    main()
