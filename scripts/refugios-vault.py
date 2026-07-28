#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
refugiOS - Secure Vault Manager (Unified interactive application)

Menu-driven application for creating, opening, closing, and deleting
encrypted LUKS vaults using dialog-based TUI.

Dependencies: python3-dialog, i18n.py
"""

import os
import sys
import subprocess
import shutil
import re
import json
import math

if not sys.stdin.isatty():
    try:
        sys.stdin = open('/dev/tty', 'r')
    except Exception:
        pass

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

HOME_DIR = os.environ.get('HOME')
if not HOME_DIR:
    print("\033[1;31m[X] ERROR:\033[0m HOME is not set. Run this script as your regular user.")
    sys.exit(1)
BASE_DIR = os.path.join(HOME_DIR, "refugiOS")
VAULT_DIR = os.path.join(BASE_DIR, "Vaults")

DESKTOP_DIR = os.path.join(HOME_DIR, "Desktop")
if not os.path.isdir(DESKTOP_DIR):
    DESKTOP_DIR = os.path.join(HOME_DIR, "Escritorio")


def log_info(msg):
    print(f"\033[1;34m[*]\033[0m {msg}")


def log_err(msg):
    print(f"\033[1;31m[X] {i18n.T('error')}:\033[0m {msg}")


def log_success(msg):
    print(f"\033[1;32m[v] {i18n.T('success')}:\033[0m {msg}")


def run_cmd(cmd, shell=True, check=True, quiet=False):
    try:
        stdout = subprocess.DEVNULL if quiet else None
        stderr = subprocess.DEVNULL if quiet else None
        subprocess.run(cmd, shell=shell, check=check, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError:
        return False
    return True


def get_cmd_output(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return result.stdout.strip()
    except Exception:
        return ""


def init_dialog():
    d = dialog.Dialog(autowidgetsize=True)
    try:
        d.add_persistent_args(["--colors"])
    except AttributeError:
        pass
    return d


def get_mapper_name(vault_name):
    return f"vault_{vault_name}"


def get_mount_point(vault_name):
    prefix = i18n.T('vault_mount_prefix')
    return os.path.join(DESKTOP_DIR, f"{prefix}_{vault_name}")


def get_desktop_file(vault_name):
    return os.path.join(DESKTOP_DIR, f"Vault_{vault_name}.desktop")


def list_all_vaults():
    if not os.path.isdir(VAULT_DIR):
        return []
    return sorted(f[:-4] for f in os.listdir(VAULT_DIR) if f.endswith('.img'))


def list_open_vaults():
    open_vaults = []
    mapper_path = "/dev/mapper"
    if os.path.isdir(mapper_path):
        for entry in os.listdir(mapper_path):
            if entry.startswith("vault_"):
                open_vaults.append(entry[6:])
    return open_vaults


def get_vault_size_mb(vault_name):
    vault_file = os.path.join(VAULT_DIR, f"{vault_name}.img")
    try:
        return os.path.getsize(vault_file) // (1024 * 1024)
    except OSError:
        return 0


def format_size(mb):
    if mb >= 1024:
        return f"{mb / 1024:.1f} GB"
    return f"{mb} MB"


def detect_usb_drives():
    usb_drives = []
    try:
        output = get_cmd_output(
            "lsblk -J -o NAME,MOUNTPOINT,SIZE,FSUSED,HOTPLUG,TYPE,TRAN 2>/dev/null"
        )
        if not output:
            return usb_drives

        data = json.loads(output)

        for device in data.get('blockdevices', []):
            is_usb = (device.get('tran') == 'usb' or device.get('hotplug') == '1'
                      or device.get('hotplug') is True)
            if not is_usb:
                continue

            children = device.get('children', [])
            if not children:
                children = [device]

            for part in children:
                mountpoint = part.get('mountpoint')
                if not mountpoint or mountpoint in ['/', '/boot', '/boot/efi', '/cdrom']:
                    continue

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
    try:
        usage = shutil.disk_usage('/')
        free_mb = usage.free // (1024 * 1024)
        safety_buffer = free_mb * 10 // 100
        max_allowed = free_mb - safety_buffer
        if required_mb <= max_allowed:
            return True, max_allowed
        else:
            return False, max(0, max_allowed)
    except Exception:
        return True, 0


def create_vault_desktop_icon(vault_name, mount_point):
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

    if shutil.which("gio"):
        checksum = get_cmd_output(f"sha256sum '{desktop_file}' | awk '{{print $1}}'")
        if checksum:
            run_cmd(f"gio set '{desktop_file}' metadata::xfce-exe-checksum '{checksum}'", quiet=True)


def remove_vault_desktop_icon(vault_name):
    desktop_file = get_desktop_file(vault_name)
    if os.path.exists(desktop_file):
        os.remove(desktop_file)


def _import_usb_to_vault(d, vault_name, vault_file, usb_info):
    mapper = get_mapper_name(vault_name)
    mount_point = get_mount_point(vault_name)

    os.system('clear')
    log_info(i18n.T('vault_importing'))

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

    usb_mount = usb_info['mountpoint']
    success = run_cmd(f"rsync -av --progress \"{usb_mount}/\" \"{mount_point}/\"")

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


def op_create(d):
    os.makedirs(VAULT_DIR, exist_ok=True)
    existing = list_all_vaults()

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

    usb_drives = detect_usb_drives()
    selected_usb = None
    suggested_size = 3072

    if usb_drives:
        usb = usb_drives[0]
        selected_usb = usb
        base_suggested = int(usb['used_mb'] * 1.5)
        usb_suggested = max(100, base_suggested)

        space_ok, max_allowed = check_root_free_space(usb_suggested)

        if space_ok:
            suggested_size = usb_suggested
            usb_info = i18n.T('vault_usb_detected').format(
                usb['device'], usb['used_mb'], suggested_size
            )
        else:
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

        space_ok, max_allowed = check_root_free_space(size_mb)
        if not space_ok:
            d.msgbox(
                i18n.T('vault_usb_no_space').format(size_mb, max_allowed),
                title=i18n.T('warning')
            )
            continue

        break

    confirm_msg = i18n.T('vault_confirm_create').format(name, size_mb)
    if d.yesno(confirm_msg, title=i18n.T('vault_create_title'),
               yes_label=i18n.T('yes'), no_label=i18n.T('no')) != d.OK:
        return

    os.system('clear')
    vault_file = os.path.join(VAULT_DIR, f"{name}.img")
    mapper = get_mapper_name(name)

    log_info(i18n.T('vault_creating'))
    print()

    if not run_cmd(f"dd if=/dev/urandom of=\"{vault_file}\" bs=1M count={size_mb} status=progress"):
        d.msgbox(i18n.T('vault_error_create'), title=i18n.T('error'))
        return

    print(f"\n\033[1;33m{i18n.T('vault_set_password')}\033[0m")
    print(f"\033[1;31m{i18n.T('vault_password_warning')}\033[0m\n")
    # --verify-passphrase overrides the verification that --batch-mode would disable:
    # without it a typo in the password makes the vault unrecoverable forever.
    if not run_cmd(f"sudo cryptsetup luksFormat --batch-mode --verify-passphrase \"{vault_file}\""):
        os.remove(vault_file)
        # La causa habitual aqui es que las dos contrasenas no coincidiesen
        d.msgbox(i18n.T('vault_error_password'), title=i18n.T('error'))
        return

    if not run_cmd(f"sudo cryptsetup open \"{vault_file}\" {mapper}"):
        os.remove(vault_file)
        d.msgbox(i18n.T('vault_error_create'), title=i18n.T('error'))
        return

    run_cmd(f"sudo mkfs.ext4 /dev/mapper/{mapper}", quiet=True)
    run_cmd(f"sudo cryptsetup close {mapper}", quiet=True)

    log_success(i18n.T('vault_created_ok').format(name))

    if selected_usb and size_mb >= selected_usb['used_mb']:
        if d.yesno(i18n.T('vault_import_usb_prompt'),
                   title=i18n.T('vault_create_title'),
                   yes_label=i18n.T('yes'), no_label=i18n.T('no')) == d.OK:
            _import_usb_to_vault(d, name, vault_file, selected_usb)

    d.msgbox(i18n.T('vault_created_ok').format(name), title=i18n.T('success'))


def op_open(d, vault_name):
    vault_file = os.path.join(VAULT_DIR, f"{vault_name}.img")
    mapper = get_mapper_name(vault_name)
    mount_point = get_mount_point(vault_name)

    if d.yesno(
        i18n.T('vault_confirm_open').format(vault_name),
        title=i18n.T('vault_open_title'),
        yes_label=i18n.T('yes'), no_label=i18n.T('no')
    ) != d.OK:
        return

    os.system('clear')
    log_info(i18n.T('vault_open').format(vault_name))

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

    create_vault_desktop_icon(vault_name, mount_point)

    log_success(i18n.T('vault_opened_ok').format(vault_name))

    d.msgbox(
        i18n.T('vault_opened_ok').format(vault_name) + "\n\n" +
        i18n.T('vault_desktop_icon_info'),
        title=i18n.T('vault_open_title')
    )


def _close_vault(vault_name):
    mapper = get_mapper_name(vault_name)
    mount_point = get_mount_point(vault_name)

    log_info(i18n.T('vault_close').format(vault_name))

    run_cmd(f"sudo umount \"{mount_point}\" 2>/dev/null", quiet=True)
    run_cmd(f"sudo cryptsetup close {mapper} 2>/dev/null", quiet=True)

    if os.path.isdir(mount_point):
        try:
            os.rmdir(mount_point)
        except OSError:
            pass

    remove_vault_desktop_icon(vault_name)

    log_success(i18n.T('vault_closed_ok').format(vault_name))


def op_close(d, vault_name):
    if d.yesno(
        i18n.T('vault_confirm_close').format(vault_name),
        title=i18n.T('vault_close_title'),
        yes_label=i18n.T('yes'), no_label=i18n.T('no')
    ) != d.OK:
        return

    os.system('clear')
    _close_vault(vault_name)
    d.msgbox(i18n.T('vault_closed_ok').format(vault_name), title=i18n.T('success'))


def op_delete(d, vault_name):
    open_vaults = list_open_vaults()
    if vault_name in open_vaults:
        d.msgbox(
            i18n.T('vault_cant_delete_open').format(vault_name),
            title=i18n.T('vault_delete_title')
        )
        return

    if d.yesno(
        i18n.T('vault_delete_confirm').format(vault_name),
        title=i18n.T('vault_delete_title'),
        yes_label=i18n.T('yes'), no_label=i18n.T('no'),
        defaultno=True
    ) != d.OK:
        return

    os.system('clear')
    vault_file = os.path.join(VAULT_DIR, f"{vault_name}.img")
    try:
        if os.path.exists(vault_file):
            os.remove(vault_file)
        remove_vault_desktop_icon(vault_name)
        log_success(i18n.T('vault_deleted_ok').format(vault_name))
        d.msgbox(i18n.T('vault_deleted_ok').format(vault_name), title=i18n.T('success'))
    except Exception:
        log_err(i18n.T('vault_delete_error').format(vault_name))
        d.msgbox(i18n.T('vault_delete_error').format(vault_name), title=i18n.T('error'))


def vault_submenu(d, vault_name, is_open):
    status = i18n.T('vault_status_open') if is_open else i18n.T('vault_status_closed')
    size_str = format_size(get_vault_size_mb(vault_name))

    choices = []
    if is_open:
        choices.append(("close", i18n.T('vault_sub_close')))
    else:
        choices.append(("open", i18n.T('vault_sub_open')))
        choices.append(("delete", i18n.T('vault_sub_delete')))
    choices.append(("back", i18n.T('vault_sub_back')))

    code, tag = d.menu(
        f"{vault_name}  [{status}]  ({size_str})",
        choices=choices,
        title=i18n.T('vault_title')
    )

    if code != d.OK or tag == "back":
        return

    if tag == "open":
        op_open(d, vault_name)
    elif tag == "close":
        op_close(d, vault_name)
    elif tag == "delete":
        op_delete(d, vault_name)


def main_menu(d):
    all_vaults = list_all_vaults()
    open_vaults = list_open_vaults()

    choices = []

    for v in all_vaults:
        status = i18n.T('vault_status_open') if v in open_vaults else i18n.T('vault_status_closed')
        size_str = format_size(get_vault_size_mb(v))
        label = f"{v}  [{status}]  ({size_str})"
        choices.append((f"V_{v}", label))

    choices.append(("create", i18n.T('vault_menu_create')))
    choices.append(("exit", i18n.T('vault_menu_exit')))

    code, tag = d.menu(i18n.T('vault_title'), choices=choices, title="refugiOS")

    if code != d.OK or tag == "exit":
        return False

    if tag == "create":
        op_create(d)
        return True

    if tag.startswith("V_"):
        vault_name = tag[2:]
        vault_submenu(d, vault_name, vault_name in open_vaults)
        return True

    return False


def main():
    if os.geteuid() == 0:
        log_err("This script should not be run as root. Run it as your regular user.")
        sys.exit(1)

    d = init_dialog()
    while main_menu(d):
        pass


if __name__ == "__main__":
    main()
