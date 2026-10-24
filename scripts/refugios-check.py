#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
refugiOS - System Check (works without any connection)

Checks that what the installer left on this device is complete and intact:
knowledge books, AI engine and models, offline maps, translator, vaults and
free space. Meant to be run before an emergency, and again after copying or
cloning the drive.

The quick check looks for interrupted downloads, broken links and missing
pieces. The full check also recomputes the checksums the installer saved next
to every file, which reads the whole drive and can take a long time.

    refugios-check.py                     interactive (dialog)
    refugios-check.py --quick|--full --no-dialog   report on stdout

Dependencies: python3-dialog (interactive mode only), i18n.py
"""

import os
import sys
import re
import json
import shutil
import hashlib
import base64
import subprocess

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

HOME_DIR = os.environ.get('HOME', '')
BASE_DIR = os.path.join(HOME_DIR, "refugiOS")
REPORT_FILE = os.path.join(BASE_DIR, "check-report.txt")

ORGANIC_MAPS_ID = "app.organicmaps.desktop"
TRANSLATOR_ID = "dev.ters.LocalTranslate"

# Minimum usable memory (RAM + VRAM - 2 GB) per model.
# Keep in sync with the register_model calls in refugios-ai-selector.sh.
MODEL_MIN_USABLE_MB = {
    "minimal-model.gguf": 1024,
    "basic-model.gguf": 6144,
    "intermediate-model.gguf": 6144,
    "advanced-model.gguf": 10240,
    "ultra-model.gguf": 18432,
}
SAFETY_MARGIN_MB = 2048
LOW_SPACE_MB = 1024

OK, WARN, FAIL = "ok", "warn", "fail"
MARKS = {OK: "[OK]", WARN: "[!!]", FAIL: "[XX]"}


class Report:
    def __init__(self):
        self.lines = []
        self.counts = {OK: 0, WARN: 0, FAIL: 0}

    def section(self, title):
        self.lines.append("")
        self.lines.append(f"== {title} ==")

    def add(self, status, text):
        self.counts[status] += 1
        self.lines.append(f"{MARKS[status]} {text}")
        print(f"{MARKS[status]} {text}", flush=True)

    def text(self):
        summary = i18n.T('chk_summary').format(self.counts[OK], self.counts[WARN], self.counts[FAIL])
        advice = i18n.T('chk_advice_fail') if self.counts[FAIL] else (
            i18n.T('chk_advice_warn') if self.counts[WARN] else i18n.T('chk_advice_ok'))
        return "\n".join([summary, advice] + self.lines) + "\n"


def human_size(n_bytes):
    mb = n_bytes / (1024 * 1024)
    return f"{mb / 1024:.1f} GB" if mb >= 1024 else f"{mb:.0f} MB"


def file_hash(path, algo):
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h


def saved_sha256(path):
    """Checksum the installer wrote next to the file, or None."""
    try:
        with open(path + ".sha256") as f:
            m = re.match(r'\s*([0-9a-fA-F]{64})', f.read())
        return m.group(1).lower() if m else None
    except OSError:
        return None


def check_file(report, path, full):
    """Common checks for a downloaded book or model. Returns True if usable."""
    name = os.path.basename(path)
    if os.path.exists(path + ".aria2"):
        report.add(FAIL, i18n.T('chk_incomplete').format(name))
        return False
    size = os.path.getsize(path)
    if size == 0:
        report.add(FAIL, i18n.T('chk_empty').format(name))
        return False
    expected = saved_sha256(path) if full else None
    if expected:
        print(i18n.T('chk_hashing').format(name), flush=True)
        if file_hash(path, 'sha256').hexdigest() != expected:
            report.add(FAIL, i18n.T('chk_corrupt').format(name))
            return False
        report.add(OK, i18n.T('chk_verified').format(name, human_size(size)))
    else:
        report.add(OK, i18n.T('chk_present').format(name, human_size(size)))
    return True


def check_links(report, folder):
    """Stable names (wikipedia.zim, basic-model.gguf...) must point to a real file."""
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.islink(path) and not os.path.exists(path):
            report.add(FAIL, i18n.T('chk_broken_link').format(name))


def check_knowledge(report, full):
    report.section(i18n.T('chk_section_books'))
    versions = os.path.join(BASE_DIR, "Knowledge", "versions")
    books = sorted(f for f in os.listdir(versions) if f.endswith('.zim')) if os.path.isdir(versions) else []
    if not books:
        report.add(WARN, i18n.T('chk_no_books'))
        return
    for name in books:
        check_file(report, os.path.join(versions, name), full)
    check_links(report, os.path.join(BASE_DIR, "Knowledge"))
    if not find_kiwix():
        report.add(FAIL, i18n.T('chk_no_kiwix'))


def find_kiwix():
    if shutil.which("kiwix-desktop"):
        return True
    apps = os.path.join(BASE_DIR, "Apps")
    for root in (apps, os.path.join(apps, "versions")):
        if os.path.isdir(root) and any(f.lower().startswith("kiwix-desktop") and f.endswith(".appimage")
                                       for f in os.listdir(root)):
            return True
    return flatpak_installed("org.kiwix.desktop")


def flatpak_installed(app_id):
    if not shutil.which("flatpak"):
        return False
    return subprocess.call(["flatpak", "info", app_id], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0


def usable_memory_mb():
    ram = 0
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    ram = int(line.split()[1]) // 1024
    except OSError:
        pass
    vram = 0
    for card in sorted(os.listdir('/sys/class/drm')) if os.path.isdir('/sys/class/drm') else []:
        try:
            with open(f'/sys/class/drm/{card}/device/mem_info_vram_total') as f:
                vram = max(vram, int(f.read().strip()) // (1024 * 1024))
        except (OSError, ValueError):
            continue
    return ram, ram + vram - SAFETY_MARGIN_MB


def check_ai(report, full):
    report.section(i18n.T('chk_section_ai'))
    ai = os.path.join(BASE_DIR, "AI")
    versions = os.path.join(ai, "versions")
    models = sorted(f for f in os.listdir(versions) if f.endswith('.gguf')) if os.path.isdir(versions) else []
    if not models:
        report.add(WARN, i18n.T('chk_no_models'))
        return
    for name in models:
        check_file(report, os.path.join(versions, name), full)
    check_links(report, ai)

    engine = os.path.join(ai, "llamafile")
    if not (os.path.isfile(engine) and os.access(engine, os.X_OK)):
        report.add(FAIL, i18n.T('chk_no_engine'))

    ram, usable = usable_memory_mb()
    fitting = [link for link, need in MODEL_MIN_USABLE_MB.items()
               if os.path.exists(os.path.join(ai, link)) and usable >= need]
    if fitting:
        report.add(OK, i18n.T('chk_ai_fits').format(ram, len(fitting)))
    else:
        report.add(WARN, i18n.T('chk_ai_too_big').format(ram))


def organic_maps_dirs():
    base = os.path.join(HOME_DIR, ".var", "app", ORGANIC_MAPS_ID, "data")
    return [os.path.join(base, "OrganicMaps"), os.path.join(base, "OMaps")]


def organic_maps_regions():
    """
    (data version, {region id: entry}) from the countries.txt bundled with the
    installed app. Sizes and hashes only apply to maps of that same version.
    """
    try:
        location = subprocess.run(["flatpak", "info", "--show-location", ORGANIC_MAPS_ID],
                                  capture_output=True, text=True).stdout.strip()
        with open(os.path.join(location, "files", "share", "organicmaps", "data", "countries.txt"),
                  encoding="utf-8") as f:
            tree = json.load(f)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None, {}
    regions = {}

    def walk(node):
        if node.get('g'):
            for child in node['g']:
                walk(child)
        else:
            regions[node['id']] = node
    walk(tree)
    return str(tree.get('v')), regions


def map_region_status(path, version, regions, full):
    """OK, or FAIL for an interrupted, truncated or corrupted region."""
    if os.path.exists(path + ".aria2"):
        return FAIL
    leaf = regions.get(os.path.basename(path)[:-4])
    if not leaf or os.path.basename(os.path.dirname(path)) != version:
        return OK
    if leaf.get('s') and leaf['s'] != os.path.getsize(path):
        return FAIL
    if full and leaf.get('sha1_base64'):
        print(i18n.T('chk_hashing').format(os.path.basename(path)), flush=True)
        if base64.b64encode(file_hash(path, 'sha1').digest()).decode() != leaf['sha1_base64']:
            return FAIL
    return OK


def check_maps(report, full):
    report.section(i18n.T('chk_section_maps'))
    if not flatpak_installed(ORGANIC_MAPS_ID):
        report.add(WARN, i18n.T('chk_no_maps_app'))
        return
    files = []
    for data_dir in organic_maps_dirs():
        if not os.path.isdir(data_dir):
            continue
        for version in os.listdir(data_dir):
            vdir = os.path.join(data_dir, version)
            if version.isdigit() and os.path.isdir(vdir):
                files += [os.path.join(vdir, f) for f in os.listdir(vdir)
                          if f.endswith('.mwm') and not f.startswith('World')]
    if not files:
        report.add(WARN, i18n.T('chk_no_maps'))
        return
    version, regions = organic_maps_regions()
    good = 0
    total = 0
    for path in sorted(files):
        if map_region_status(path, version, regions, full) == FAIL:
            report.add(FAIL, i18n.T('chk_corrupt').format(os.path.basename(path)))
        else:
            good += 1
            total += os.path.getsize(path)
    if good:
        report.add(OK, i18n.T('chk_maps_ok').format(good, human_size(total)))


def check_translator(report):
    launcher_names = ("Translator.desktop",)
    desktop = desktop_dir()
    has_launcher = any(os.path.exists(os.path.join(desktop, n)) for n in launcher_names)
    if flatpak_installed(TRANSLATOR_ID):
        report.section(i18n.T('chk_section_translator'))
        report.add(OK, i18n.T('chk_translator_ok'))
    elif has_launcher:
        report.section(i18n.T('chk_section_translator'))
        report.add(FAIL, i18n.T('chk_translator_missing'))


def desktop_dir():
    d = os.path.join(HOME_DIR, "Desktop")
    return d if os.path.isdir(d) else os.path.join(HOME_DIR, "Escritorio")


def check_vaults(report):
    vaults_dir = os.path.join(BASE_DIR, "Vaults")
    vaults = sorted(f for f in os.listdir(vaults_dir) if f.endswith('.img')) if os.path.isdir(vaults_dir) else []
    if not vaults:
        return
    report.section(i18n.T('chk_section_vaults'))
    for name in vaults:
        try:
            with open(os.path.join(vaults_dir, name), 'rb') as f:
                magic = f.read(6)
        except OSError:
            magic = b''
        if magic == b'LUKS\xba\xbe':
            report.add(OK, i18n.T('chk_vault_ok').format(name[:-4]))
        else:
            report.add(FAIL, i18n.T('chk_vault_bad').format(name[:-4]))
    report.add(WARN, i18n.T('chk_vault_password'))


def check_space(report):
    report.section(i18n.T('chk_section_space'))
    free_mb = shutil.disk_usage(HOME_DIR or '/').free // (1024 * 1024)
    status = WARN if free_mb < LOW_SPACE_MB else OK
    report.add(status, i18n.T('chk_free_space').format(human_size(free_mb * 1024 * 1024)))


def run_checks(full):
    report = Report()
    check_knowledge(report, full)
    check_ai(report, full)
    check_maps(report, full)
    check_translator(report)
    check_vaults(report)
    check_space(report)
    return report


def sanitize_for_dialog(text):
    for a, b in {'•': '-', '–': '-', '—': '--', '‘': "'", '’': "'",
                 '“': '"', '”': '"', '…': '...'}.items():
        text = text.replace(a, b)
    return text.encode('latin-1', 'replace').decode('latin-1')


def main():
    args = sys.argv[1:]
    use_dialog = "--no-dialog" not in args
    full = "--full" in args

    if use_dialog:
        try:
            import dialog
        except ImportError:
            print(i18n.T('dialog_error'))
            sys.exit(1)
        d = dialog.Dialog(autowidgetsize=True)
        if "--quick" not in args and "--full" not in args:
            code, tag = d.menu(sanitize_for_dialog(i18n.T('chk_intro')), title=sanitize_for_dialog(i18n.T('chk_title')),
                               choices=[("1", sanitize_for_dialog(i18n.T('chk_mode_quick'))),
                                        ("2", sanitize_for_dialog(i18n.T('chk_mode_full')))])
            if code != d.OK:
                sys.exit(0)
            full = tag == "2"
        os.system('clear')

    print(i18n.T('chk_running'), flush=True)
    report = run_checks(full)
    text = report.text()
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError:
        pass

    if use_dialog:
        d.scrollbox(sanitize_for_dialog(text + "\n" + i18n.T('chk_report_saved').format(REPORT_FILE)),
                    title=sanitize_for_dialog(i18n.T('chk_title')), height=30, width=100)
        os.system('clear')
    else:
        print()
        print(text)
    sys.exit(1 if report.counts[FAIL] else 0)


if __name__ == "__main__":
    main()
