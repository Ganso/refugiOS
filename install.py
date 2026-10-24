#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
refugiOS - System Installer (Python)
(Environment and applications preparation)

Extended Description:
This script prepares the base operating system for refugiOS use.
It automates downloading and installing base tools, packages in various formats
(AppImage, Flatpak, APT), offline knowledge bases (Wikipedia, WikiMed, etc.),
conditional download of local execution AI models (LLMs),
and creation of secure cryptographic environments (Vaults).

The script requires execution as a normal user (NOT root) and will request
the password for local elevation via `sudo` when system modification is needed.
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import json
import hashlib
import base64
import shutil
import re
import time
import random

# Localization system
try:
    import i18n
except ImportError:
    # If not in path, try current directory
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
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
# RESOURCE CONFIGURATION (ZIM AND AI)
# ==============================================================================

# Knowledge Databases (ZIM)
# Entries hold i18n keys, not translated text: the user may switch language
# after this module has been imported. A "{lang}" placeholder in a stem is
# replaced by the user's language, falling back to English when the book does
# not exist in it. Stems without the placeholder are single-language books.
# Sizes are approximate MB per language, used for the space estimate.
KIWIX_ZIM = "https://download.kiwix.org/zim/"

WIKIPEDIA_CONFIG = [
    {"id": "wiki_lite", "label_key": "wiki_lite_label", "stem": "wikipedia_{lang}_top_mini",
     "urls": [KIWIX_ZIM + "wikipedia/"], "priority": 1, "size_mb": {"es": 210, "en": 290}},
    {"id": "wiki_top_nopic", "label_key": "wiki_top_nopic_label", "stem": "wikipedia_{lang}_top_nopic",
     "urls": [KIWIX_ZIM + "wikipedia/"], "priority": 2, "size_mb": {"es": 1150, "en": 2700}},
    {"id": "wiki_top_maxi", "label_key": "wiki_top_maxi_label", "stem": "wikipedia_{lang}_top_maxi",
     "urls": [KIWIX_ZIM + "wikipedia/"], "priority": 3, "size_mb": {"es": 3900, "en": 6700}},
    {"id": "wiki_nopics", "label_key": "wiki_nopics_label", "stem": "wikipedia_{lang}_all_nopic",
     "urls": [KIWIX_ZIM + "wikipedia/"], "priority": 4, "size_mb": {"es": 12300, "en": 50200}},
    {"id": "wiki_total", "label_key": "wiki_total_label", "stem": "wikipedia_{lang}_all_maxi",
     "urls": [KIWIX_ZIM + "wikipedia/"], "priority": 5, "size_mb": {"es": 34800, "en": 121900}},
]

# Menu groups for the rest of the library, shown as one checklist each
LIBRARY_GROUPS = [
    {"id": "health", "title_key": "lib_group_health"},
    {"id": "survival", "title_key": "lib_group_survival"},
    {"id": "practical", "title_key": "lib_group_practical"},
    {"id": "culture", "title_key": "lib_group_culture"},
]

# "desktop": True puts the launcher on the desktop itself; the rest go into
# the library folder so the desktop stays readable.
# "only_langs" hides a book from users of other languages.
# "presets" lists the storage modes (lite/standard/rich) that preselect it.
LIBRARY_CATALOG = [
    # Health
    {"id": "wikimed", "group": "health", "label_key": "lib_wikimed", "title_key": "lib_wikimed_title",
     "stem": "wikipedia_{lang}_medicine_maxi", "urls": [KIWIX_ZIM + "wikipedia/"],
     "size_mb": {"es": 450, "en": 1750}, "symlink": "wikimed.zim", "desktop": True,
     "presets": ["lite", "standard", "rich"]},
    {"id": "wikem", "group": "health", "label_key": "lib_wikem", "title_key": "lib_wikem_title",
     "stem": "wikem_en_all_maxi", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 260, "presets": ["standard", "rich"]},
    {"id": "zimgit_medicine", "group": "health", "label_key": "lib_zimgit_medicine", "title_key": "lib_zimgit_medicine_title",
     "stem": "zimgit-medicine_en", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 70, "presets": ["lite", "standard", "rich"]},
    # Emergencies and survival
    {"id": "post_disaster", "group": "survival", "label_key": "lib_post_disaster", "title_key": "lib_post_disaster_title",
     "stem": "zimgit-post-disaster_en", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 620, "presets": ["standard", "rich"]},
    {"id": "water", "group": "survival", "label_key": "lib_water", "title_key": "lib_water_title",
     "stem": "zimgit-water_en", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 20, "presets": ["lite", "standard", "rich"]},
    {"id": "food", "group": "survival", "label_key": "lib_food", "title_key": "lib_food_title",
     "stem": "zimgit-food-preparation_en", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 95, "presets": ["lite", "standard", "rich"]},
    {"id": "knots", "group": "survival", "label_key": "lib_knots", "title_key": "lib_knots_title",
     "stem": "zimgit-knots_en", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 30, "presets": ["lite", "standard", "rich"]},
    {"id": "scoutwiki", "group": "survival", "label_key": "lib_scoutwiki", "title_key": "lib_scoutwiki_title",
     "stem": "scoutwiki.org_es_all_maxi", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 20, "only_langs": ["es"], "presets": ["lite", "standard", "rich"]},
    {"id": "outdoors", "group": "survival", "label_key": "lib_outdoors", "title_key": "lib_outdoors_title",
     "stem": "outdoors.stackexchange.com_en_all", "urls": [KIWIX_ZIM + "stack_exchange/"],
     "size_mb": 140, "presets": ["standard", "rich"]},
    {"id": "wikihow", "group": "survival", "label_key": "lib_wikihow", "title_key": "lib_wikihow_title",
     "stem": "wikihow_{lang}_maxi",
     "urls": [
         "https://download.kiwix.org/archive/zim/wikihow/",
         "https://mirror-sites-ca.mblibrary.info/mirror-sites/download.kiwix.org/archive/zim/wikihow/",
         "https://mirror.netcologne.de/kiwix/zim/wikihow/",
     ],
     "size_mb": {"es": 25600, "en": 49200}, "symlink": "wikihow.zim", "desktop": True,
     "presets": ["rich"]},
    # Practical knowledge
    {"id": "ifixit", "group": "practical", "label_key": "lib_ifixit", "title_key": "lib_ifixit_title",
     "stem": "ifixit_{lang}_all", "urls": [KIWIX_ZIM + "ifixit/"],
     "size_mb": 3500, "presets": ["rich"]},
    {"id": "appropedia", "group": "practical", "label_key": "lib_appropedia", "title_key": "lib_appropedia_title",
     "stem": "appropedia_en_all_maxi", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 560, "presets": ["rich"]},
    {"id": "energypedia", "group": "practical", "label_key": "lib_energypedia", "title_key": "lib_energypedia_title",
     "stem": "energypedia_en_all_maxi", "urls": [KIWIX_ZIM + "other/"],
     "size_mb": 770, "presets": ["rich"]},
    {"id": "gardening", "group": "practical", "label_key": "lib_gardening", "title_key": "lib_gardening_title",
     "stem": "gardening.stackexchange.com_en_all", "urls": [KIWIX_ZIM + "stack_exchange/"],
     "size_mb": 900, "presets": ["rich"]},
    {"id": "diy", "group": "practical", "label_key": "lib_diy", "title_key": "lib_diy_title",
     "stem": "diy.stackexchange.com_en_all", "urls": [KIWIX_ZIM + "stack_exchange/"],
     "size_mb": 1950, "presets": []},
    {"id": "mechanics", "group": "practical", "label_key": "lib_mechanics", "title_key": "lib_mechanics_title",
     "stem": "mechanics.stackexchange.com_en_all", "urls": [KIWIX_ZIM + "stack_exchange/"],
     "size_mb": 330, "presets": []},
    {"id": "ham", "group": "practical", "label_key": "lib_ham", "title_key": "lib_ham_title",
     "stem": "ham.stackexchange.com_en_all", "urls": [KIWIX_ZIM + "stack_exchange/"],
     "size_mb": 75, "presets": ["standard", "rich"]},
    # Language, culture and education
    {"id": "wiktionary", "group": "culture", "label_key": "lib_wiktionary", "title_key": "lib_wiktionary_title",
     "stem": "wiktionary_{lang}_all_nopic", "urls": [KIWIX_ZIM + "wiktionary/"],
     "size_mb": {"es": 640, "en": 8700}, "presets": ["standard", "rich"]},
    {"id": "wikivoyage", "group": "culture", "label_key": "lib_wikivoyage", "title_key": "lib_wikivoyage_title",
     "stem": "wikivoyage_{lang}_all_maxi", "urls": [KIWIX_ZIM + "wikivoyage/"],
     "size_mb": {"es": 140, "en": 1050}, "presets": ["lite", "standard", "rich"]},
    {"id": "wikibooks", "group": "culture", "label_key": "lib_wikibooks", "title_key": "lib_wikibooks_title",
     "stem": "wikibooks_{lang}_all_maxi", "urls": [KIWIX_ZIM + "wikibooks/"],
     "size_mb": {"es": 340, "en": 5900}, "presets": ["rich"]},
    {"id": "wikisource", "group": "culture", "label_key": "lib_wikisource", "title_key": "lib_wikisource_title",
     "stem": "wikisource_{lang}_all_nopic", "urls": [KIWIX_ZIM + "wikisource/"],
     "size_mb": {"es": 390, "en": 3700}, "presets": ["rich"]},
    {"id": "gutenberg", "group": "culture", "label_key": "lib_gutenberg", "title_key": "lib_gutenberg_title",
     "stem": "gutenberg_es_all", "urls": [KIWIX_ZIM + "gutenberg/"],
     "size_mb": 1750, "only_langs": ["es"], "presets": ["rich"]},
    {"id": "phet", "group": "culture", "label_key": "lib_phet", "title_key": "lib_phet_title",
     "stem": "phet_{lang}_all", "urls": [KIWIX_ZIM + "phet/"],
     "size_mb": 110, "presets": ["standard", "rich"]},
]

# Offline maps for Organic Maps. Each preset is a list of top-level country ids
# from the countries.txt bundled with the app; every region below them is
# downloaded. Sizes are approximate MB, for the space estimate only.
MAP_EUROPE = [
    "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina",
    "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
    "Faroe Islands", "Finland", "France", "Germany", "Gibraltar", "Greece",
    "Guernsey", "Hungary", "Iceland", "Ireland", "Isle of Man", "Italy", "Jersey",
    "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta",
    "Moldova", "Monaco", "Montenegro", "Netherlands", "Norway", "Poland",
    "Portugal", "Republic of Kosovo", "Romania", "San Marino", "Serbia",
    "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine",
    "United Kingdom",
]

MAP_PRESETS = [
    {"id": "map_spain", "label_key": "map_spain", "countries": ["Spain", "Andorra", "Gibraltar"], "size_mb": 1800},
    {"id": "map_portugal", "label_key": "map_portugal", "countries": ["Portugal"], "size_mb": 470},
    {"id": "map_europe", "label_key": "map_europe", "countries": MAP_EUROPE, "size_mb": 32000},
    {"id": "map_mexico", "label_key": "map_mexico", "countries": ["Mexico"], "size_mb": 730},
    {"id": "map_colombia", "label_key": "map_colombia", "countries": ["Colombia"], "size_mb": 320},
    {"id": "map_argentina", "label_key": "map_argentina", "countries": ["Argentina"], "size_mb": 800},
    {"id": "map_chile", "label_key": "map_chile", "countries": ["Chile"], "size_mb": 440},
    {"id": "map_peru", "label_key": "map_peru", "countries": ["Peru"], "size_mb": 280},
    {"id": "map_venezuela", "label_key": "map_venezuela", "countries": ["Venezuela"], "size_mb": 130},
    {"id": "map_brazil", "label_key": "map_brazil", "countries": ["Brazil"], "size_mb": 2300},
    {"id": "map_usa", "label_key": "map_usa", "countries": ["United States of America"], "size_mb": 15200},
]

# Offline translator: Firefox's neural translation models, bundled in the Flatpak
TRANSLATOR_ID = "dev.ters.LocalTranslate"
TRANSLATOR_SIZE_MB = 2700

# Spell checking and hyphenation for LibreOffice, gedit and the browser
SPELLING_PACKAGES = {
    "es": "hunspell-es hyphen-es mythes-es",
    "en": "hunspell-en-us hyphen-en-us mythes-en-us",
}

ORGANIC_MAPS_ID = "app.organicmaps.desktop"
ORGANIC_MAPS_META = "https://meta.omaps.app/maps"
ORGANIC_MAPS_FALLBACK_SERVERS = ["https://cdn-us1.organicmaps.app/"]

# Artificial Intelligence Models (GGUF)
AI_MODEL_CONFIG = [
    {
        "id": "ia_min",
        "label_key": "ia_min_label",
        "filename": "Qwen3-0.6B-Q4_K_M.gguf",
        "url": "https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf",
        "symlink": "minimal-model.gguf",
        "size_mb": 380
    },
    {
        "id": "ia_base",
        "label_key": "ia_base_label",
        "filename": "gemma-4-E4B-it-Q4_K_M.gguf",
        "url": "https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf",
        "symlink": "basic-model.gguf",
        "size_mb": 4750
    },
    {
        "id": "ia_med",
        "label_key": "ia_med_label",
        "filename": "Qwen3-8B-Q4_K_M.gguf",
        "url": "https://huggingface.co/unsloth/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf",
        "symlink": "intermediate-model.gguf",
        "size_mb": 4800
    },
    {
        "id": "ia_max",
        "label_key": "ia_max_label",
        "filename": "Qwen3-14B-Q4_K_M.gguf",
        "url": "https://huggingface.co/unsloth/Qwen3-14B-GGUF/resolve/main/Qwen3-14B-Q4_K_M.gguf",
        "symlink": "advanced-model.gguf",
        "size_mb": 8600
    },
    {
        "id": "ia_ultra",
        "label_key": "ia_ultra_label",
        "filename": "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf",
        "url": "https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/resolve/main/gemma-4-26B-A4B-it-UD-Q4_K_M.gguf",
        "symlink": "ultra-model.gguf",
        "size_mb": 16200
    }
]

# ==============================================================================
# SECTION 1: UTILITY FUNCTIONS AND LOGS
# ==============================================================================

FAILED_ITEMS = []

def _write_log(msg):
    # Remove ANSI color codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_msg = ansi_escape.sub('', msg)
    try:
        with open("/tmp/refugios-install.log", 'a') as f:
            f.write(clean_msg + "\n")
    except:
        pass

def log_info(msg):
    """Displays an informative message in blue."""
    print(f"\033[1;34m[*]\033[0m {msg}")
    _write_log(f"[*] {msg}")

def log_err(msg, fatal=True):
    """Displays a critical error message in red and optionally terminates execution."""
    prefix = f"[X] {i18n.T('error')}:"
    print(f"\033[1;31m{prefix}\033[0m {msg}")
    _write_log(f"{prefix} {msg}")
    if fatal:
        sys.exit(1)
    else:
        FAILED_ITEMS.append(msg)

def log_success(msg):
    """Displays a success message in green."""
    prefix = f"[v] {i18n.T('success')}:"
    print(f"\033[1;32m{prefix}\033[0m {msg}")
    _write_log(f"{prefix} {msg}")

class SizeLogger:
    """Tracks disk space usage across installation phases."""
    def __init__(self):
        self.initial_space = self._get_free_space()
        self.last_space = self.initial_space
        _write_log("=== refugiOS Installation Size Log ===")
            
    def _get_free_space(self):
        try:
            os.sync()
            stat = shutil.disk_usage('/')
            return stat.free // (1024 * 1024)
        except:
            return 0
            
    def log_section(self, section_name):
        current_space = self._get_free_space()
        used_mb = self.last_space - current_space
        self.last_space = current_space
        log_info(f"[Size Log] [{section_name}] Espacio ocupado: {used_mb} MB")

    def log_total(self):
        current_space = self._get_free_space()
        total_used = self.initial_space - current_space
        log_info(f"[Size Log] [TOTAL] Espacio total ocupado: {total_used} MB")
        return total_used


def run_cmd(cmd, shell=True, check=True, quiet=False):
    """
    Executes a command in the system terminal.
    :param cmd: The command to execute (string).
    :param shell: If True, execute through a shell (allows pipes, etc).
    :param check: If True, raise exception if command fails.
    :param quiet: If True, redirect stdout and stderr to DEVNULL for cleaner logs.
    :return: True if command succeeded, False otherwise.
    """
    try:
        stdout = subprocess.DEVNULL if quiet else None
        stderr = subprocess.DEVNULL if quiet else None
        subprocess.run(cmd, shell=shell, check=check, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError:
        if not quiet:
            print(f"\033[1;33m[!] {i18n.T('warning')}:\033[0m Command failed attempting to execute: {cmd}")
        return False
    return True

def download_with_aria2(url, dest_path, timeout=120, max_tries=3, keep_partial=True):
    """
    Descarga con aria2c: multi-conexion, deteccion de estancamiento, reintentos.
    -x 8 -s 8: 8 conexiones paralelas + 8 splits
    --timeout / --connect-timeout: detectan la conexion muerta (limite real)
    --max-tries: reintentos por conexion
    El parametro 'timeout' es solo una red de seguridad muy holgada frente a una
    congelacion del proceso, NO un limite de duracion de la descarga: en conexiones
    lentas un modelo de varios GB tarda horas legitimamente.
    En caso de fallo se conserva el fichero parcial y su control .aria2, que es lo
    que permite a --continue=true reanudar en la siguiente ejecucion. Con
    keep_partial=False el parcial se descarta: solo para ficheros pequenos, donde
    reanudar no aporta nada y un resto truncado podria confundirse con uno valido.
    """
    dest_dir = os.path.dirname(dest_path)
    filename = os.path.basename(dest_path)
    aria2_control = dest_path + ".aria2"

    # Red de seguridad: como minimo 6 horas, o lo que pida el llamante si es mayor
    hard_limit = max(timeout, 21600)

    cmd = (
        f"timeout {hard_limit} aria2c -x 8 -s 8 "
        f"--timeout=15 "
        f"--max-tries={max_tries} "
        f"--connect-timeout=10 "
        f"--continue=true "
        f"--auto-file-renaming=false "
        f"--dir=\"{dest_dir}\" "
        f"-o \"{filename}\" "
        f"\"{url}\""
    )

    success = run_cmd(cmd, quiet=True)

    try:
        if success or not keep_partial:
            if os.path.exists(aria2_control):
                os.remove(aria2_control)
        if not success and not keep_partial and os.path.exists(dest_path):
            os.remove(dest_path)
    except OSError:
        pass

    return success


def version_key(name):
    """
    Sort key that compares embedded version numbers numerically.
    Plain lexicographic order picks 2.9 over 2.10, which would install an
    outdated AppImage.
    """
    return [int(part) for part in re.findall(r'\d+', name)]

KIWIX_APPIMAGE_MIN_GLIBC = (2, 35)

def glibc_version():
    """(major, minor) of the system glibc, or None if it cannot be told."""
    try:
        version = os.confstr('CS_GNU_LIBC_VERSION').split()[1]
        return tuple(int(x) for x in version.split('.')[:2])
    except (ValueError, OSError, IndexError, AttributeError):
        return None

def get_cmd_output(cmd):
    """
    Executes a command in the terminal and returns the resulting stdout text.
    Used mainly to get hardware information.
    """
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return result.stdout.strip()
    except Exception:
        return ""

def certify_icon(fpath):
    try:
        os.chmod(fpath, 0o755)
        if shutil.which("gio"):
            checksum = get_cmd_output(f"sha256sum '{fpath}' | awk '{{print $1}}'")
            if checksum:
                run_cmd(f"gio set '{fpath}' metadata::xfce-exe-checksum '{checksum}'", quiet=True)
    except Exception as e:
        log_err(i18n.T('desktop_cert_error').format(os.path.basename(fpath), e), fatal=False)

def certify_all_desktop_icons(desktop_dir):
    """
    Recursively certifies all .desktop files in the given directory.
    Called once at the end of installation to ensure nothing was missed.
    """
    if not os.path.isdir(desktop_dir):
        return
    for fname in os.listdir(desktop_dir):
        if fname.endswith('.desktop'):
            certify_icon(os.path.join(desktop_dir, fname))
    run_cmd("xfdesktop --reload 2>/dev/null || true", quiet=True)

OBSOLETE_EXEC_PATTERNS = [
    'refugios-vault-create.sh',
    'refugios-vault-open.sh',
    'refugios-vault-close.sh',
]

def cleanup_obsolete_icons(desktop_dir):
    """
    Removes obsolete desktop icons from previous refugiOS versions.
    Detects icons by checking if their Exec line references known
    obsolete script names.
    """
    if not os.path.isdir(desktop_dir):
        return
    for fname in os.listdir(desktop_dir):
        if not fname.endswith('.desktop'):
            continue
        fpath = os.path.join(desktop_dir, fname)
        try:
            with open(fpath, 'r') as f:
                content = f.read()
            for pattern in OBSOLETE_EXEC_PATTERNS:
                if pattern in content:
                    os.remove(fpath)
                    log_info(i18n.T('obsolete_icon').format(fname))
                    break
        except Exception:
            pass

def ensure_install_icon(env, sys_info):
    """
    Creates the 'Complete refugiOS installation' wrapper script and
    desktop icon if they don't already exist.
    Allows users to re-run the installer to add more components.
    Matches the wrapper injected by build_refugios.sh exactly.
    """
    wrapper_path = "/usr/local/bin/refugios-install-wrapper.sh"
    if not os.path.exists(wrapper_path):
        # Localised strings for the wrapper (resolved at install time)
        err_title  = i18n.T('wrapper_err_title')
        err_text   = i18n.T('wrapper_err_text')
        ping_msg   = i18n.T('wrapper_ping')
        ok_msg     = i18n.T('wrapper_ok')
        console_err   = i18n.T('wrapper_console_err')
        console_text1 = i18n.T('wrapper_console_text1')
        console_text2 = i18n.T('wrapper_console_text2')
        console_text3 = i18n.T('wrapper_console_text3')
        console_prompt = i18n.T('wrapper_console_prompt')

        wrapper_content = f'''#!/bin/bash
LOG="/tmp/refugios-install.log"
echo "=== refugios-install-wrapper.sh iniciado: $(date) ===" >> "$LOG"
echo "=> {ping_msg}"
if ping -c 1 -W 3 github.com > /dev/null 2>&1; then
    echo "=> {ok_msg}"
    echo "Conexión OK, lanzando instalador..." >> "$LOG"
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh 2>>"$LOG" | bash
    echo "Instalador finalizado con código: $?" >> "$LOG"
else
    if [ -n "$DISPLAY" ] && command -v zenity > /dev/null 2>&1; then
        zenity --error \\
               --title="{err_title}" \\
               --text="{err_text}" \\
               --width=450
    else
        echo ""
        echo "=========================================================="
        echo " {console_err}"
        echo "=========================================================="
        echo " {console_text1}"
        echo " {console_text2}"
        echo " {console_text3}"
        echo "=========================================================="
        echo ""
        echo "{console_prompt}"
        read
    fi
fi
echo "=== refugios-install-wrapper.sh finalizado ===" >> "$LOG"
'''
        try:
            with open('/tmp/refugios-install-wrapper.sh', 'w') as f:
                f.write(wrapper_content)
            os.chmod('/tmp/refugios-install-wrapper.sh', 0o755)
            run_cmd("sudo cp /tmp/refugios-install-wrapper.sh /usr/local/bin/refugios-install-wrapper.sh", quiet=True)
            run_cmd("sudo chmod 755 /usr/local/bin/refugios-install-wrapper.sh", quiet=True)
            try:
                os.remove('/tmp/refugios-install-wrapper.sh')
            except OSError:
                pass
        except Exception:
            pass

    desktop_file = os.path.join(env.desktop, "Instalar_refugiOS.desktop")
    if not os.path.exists(desktop_file):
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={i18n.T('install_icon_name')}
Comment={i18n.T('install_icon_comment')}
Exec=xfce4-terminal -e "/usr/local/bin/refugios-install-wrapper.sh"
Icon=system-software-install
Terminal=false
Categories=System;
""")
        certify_icon(desktop_file)


def set_wallpaper(sys_info):
    """
    Sets the desktop wallpaper to media/logo/fondo.png scaled without deformation.
    Supports XFCE and Raspberry OS (PCManFM).
    """
    try:
        msg = i18n.T('setting_wallpaper')
    except:
        msg = "Configurando fondo de pantalla..."
    log_info(msg)

    home_dir = os.environ.get('HOME', '')
    perm_wallpaper_dir = os.path.join(home_dir, "refugiOS", "System")
    os.makedirs(perm_wallpaper_dir, exist_ok=True)
    perm_wallpaper_path = os.path.join(perm_wallpaper_dir, "fondo.png")
    
    installer_dir = os.path.dirname(os.path.realpath(__file__))
    # 'logo/' is where the artwork lived before 0.23; kept so a checkout of an
    # older revision still finds the wallpaper
    local_candidates = [
        os.path.join(installer_dir, "media", "logo", "fondo.png"),
        os.path.join(installer_dir, "logo", "fondo.png"),
    ]
    local_wallpaper_path = next((p for p in local_candidates if os.path.exists(p)), None)

    if local_wallpaper_path:
        try:
            shutil.copy(local_wallpaper_path, perm_wallpaper_path)
        except Exception:
            pass
    else:
        repo_url = os.environ.get("REPO_URL", "https://raw.githubusercontent.com/Ganso/refugiOS/main")
        remote_url = f"{repo_url}/media/logo/fondo.png"
        download_with_aria2(remote_url, perm_wallpaper_path, timeout=30, keep_partial=False)

    if not os.path.exists(perm_wallpaper_path) or os.path.getsize(perm_wallpaper_path) == 0:
        return
        
        
    # XFCE
    if shutil.which("xfconf-query"):
        monitors = []
        try:
            xrandr_out = subprocess.check_output("xrandr 2>/dev/null", shell=True, text=True)
            for line in xrandr_out.splitlines():
                if " connected" in line:
                    monitors.append(line.split()[0])
        except Exception:
            pass

        try:
            xfconf_out = subprocess.check_output("xfconf-query -c xfce4-desktop -p /backdrop -l 2>/dev/null", shell=True, text=True)
            for line in xfconf_out.splitlines():
                parts = line.strip().split('/')
                if len(parts) >= 4 and parts[3].startswith('monitor'):
                    monitor_name = parts[3][7:]
                    if monitor_name:
                        monitors.append(monitor_name)
        except Exception:
            pass

        monitors.extend(["0", "1", "default"])
        monitors = sorted(list(set(monitors)))

        def set_xfconf_prop(prop, prop_type, value):
            check_cmd = f"xfconf-query -c xfce4-desktop -p {prop} >/dev/null 2>&1"
            exists = subprocess.call(check_cmd, shell=True) == 0
            if exists:
                set_cmd = f"xfconf-query -c xfce4-desktop -p {prop} -s '{value}'"
            else:
                set_cmd = f"xfconf-query -c xfce4-desktop -p {prop} --create -t {prop_type} -s '{value}'"
            subprocess.call(set_cmd, shell=True)

        for monitor in monitors:
            for workspace in [None, 0, 1, 2, 3, 4]:
                if workspace is None:
                    base = f"/backdrop/screen0/monitor{monitor}"
                else:
                    base = f"/backdrop/screen0/monitor{monitor}/workspace{workspace}"
                
                set_xfconf_prop(f"{base}/last-image", "string", perm_wallpaper_path)
                set_xfconf_prop(f"{base}/image-path", "string", perm_wallpaper_path)
                set_xfconf_prop(f"{base}/image-style", "int", "5")
                set_xfconf_prop(f"{base}/image-show", "bool", "true")

        subprocess.call("xfdesktop --reload 2>/dev/null || true", shell=True)
    
    # PCManFM (Raspberry Pi OS)
    if shutil.which("pcmanfm"):
        run_cmd(f"pcmanfm --set-wallpaper='{perm_wallpaper_path}' --wallpaper-mode=crop", quiet=True)

# ==============================================================================
# SECTION 2: SYSTEM DETECTION AND DIAGNOSIS
# ==============================================================================

class SystemInfo:
    """
    Class that collects, processes, and exposes information about the computer
    running the script (OS, RAM, Storage, GPU).
    """
    def __init__(self):
        self.os_type = "Unknown"
        self.is_rpi = False
        self.rpi_model = ""
        desktop = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION")
        session_type = os.environ.get("XDG_SESSION_TYPE")
        if desktop and session_type:
            self.desktop_env = f"{desktop} ({session_type.upper()})"
        elif desktop:
            self.desktop_env = desktop
        elif session_type:
            self.desktop_env = session_type.upper()
        else:
            self.desktop_env = "Unknown"
        self.ram_mb = 0
        self.free_space_mb = 0
        self.gpu_info = "Unknown"
        self.vram_info = "Unknown"
        self.has_nvidia = False
        self.lang = i18n.REFUGIOS_LANG
        
        self.detect_os()
        self.detect_ram()
        self.detect_storage()
        self.detect_gpu()

    def detect_os(self):
        """
        Determines if it is Ubuntu, Debian, or Raspberry Pi by inspecting Linux native files.
        """
        try:
            # Generic file present in most Linux distros
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'ID=ubuntu' in content:
                    self.os_type = "Ubuntu"
                elif 'ID=debian' in content:
                    self.os_type = "Debian"
                else:
                    m = re.search(r'^ID=([a-zA-Z0-9_]+)', content, re.MULTILINE)
                    if m: self.os_type = m.group(1).capitalize()
        except:
            pass

        try:
            # Physical models pre-recorded (typical for ARM development boards)
            # Standard path /proc/device-tree/model
            for model_path in ['/proc/device-tree/model', '/sys/firmware/devicetree/base/model']:
                try:
                    with open(model_path, 'r') as f:
                        model = f.read().rstrip('\x00').strip()
                        if 'Raspberry Pi' in model:
                            self.is_rpi = True
                            self.rpi_model = model
                            self.os_type = "Raspberry Pi OS"
                            break
                except:
                    continue
        except:
            pass

    def detect_ram(self):
        """Reads total installed RAM from /proc/meminfo in KB and converts to MB."""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        kb = int(line.split()[1])
                        self.ram_mb = kb // 1024
                        break
        except:
            pass

    def detect_storage(self):
        """Checks available disk space on the root partition (/)."""
        try:
            stat = shutil.disk_usage('/')
            self.free_space_mb = stat.free // (1024 * 1024)
        except:
            pass

    def detect_gpu(self):
        """
        Executes system calls (lspci) to determine graphics card type
        and tries to parse reserved VRAM (prefetchable memory segment).
        """
        out = get_cmd_output("lspci -v 2>/dev/null")
        if out:
            # Extract exact GPU model
            vga_match = re.search(r'(VGA compatible controller|3D controller): (.*)', out)
            if vga_match:
                self.gpu_info = vga_match.group(2).strip()
                if re.search(r'nvidia|geforce', self.gpu_info, re.IGNORECASE):
                    self.has_nvidia = True
                # Extract prefetchable memory, commonly indicating VRAM segments
                mem_match = re.search(r'Memory at .*?\(prefetchable\) \[size=([A-Za-z0-9]+)\]', out)
                if mem_match:
                    self.vram_info = mem_match.group(1)

def fix_flatpak_permissions():
    """
    Fixes 'bwrap: Creating new namespace failed: Permission denied' error
    typical in Ubuntu 24.04 and Debian 13 due to AppArmor restrictions on unprivileged namespaces.
    """
    path = "/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                if f.read().strip() == '1':
                    log_info(i18n.T('patching_apparmor'))
                    run_cmd("echo 'kernel.apparmor_restrict_unprivileged_userns = 0' | sudo tee /etc/sysctl.d/60-apparmor-namespace.conf", quiet=True)
                    run_cmd("sudo sysctl -p /etc/sysctl.d/60-apparmor-namespace.conf", quiet=True)
        except Exception as e:
            log_info(f"Notice: Could not verify/apply AppArmor patch: {e}")

def fix_rpi_pcmanfm_warnings():
    """
    Disables PCManFM warning for non-executable file shells (Raspberry Pi OS).
    Required for desktop icons calling scripts to work without prompts.
    """
    script = r"""
F="$HOME/.config/pcmanfm/default/pcmanfm.conf"
mkdir -p "$(dirname "$F")"
if [ -f "$F" ]; then
    grep -q "^\[ui\]" "$F" || echo "[ui]" >> "$F"
    sed -i '/cx_non_exec_warning/d' "$F"
    sed -i '/^\[ui\]/a cx_non_exec_warning=0' "$F"
else
    echo -e "[ui]\ncx_non_exec_warning=0" > "$F"
fi
pcmanfm --reconfigure
"""
    log_info(i18n.T('optimizing_pcmanfm'))
    run_cmd(script, quiet=True)

# ==============================================================================
# SECTION 3: MULTIPLE INTERACTION MENUS (TUI with pythondialog)
# ==============================================================================

def sanitize_for_dialog(text):
    """
    Sanitizes text for dialog (latin-1) compatibility.
    The dialog library encodes strings using latin-1, which cannot represent
    certain Unicode characters (e.g. U+2022 bullet). This function replaces
    common Unicode typographic characters with ASCII equivalents and encodes
    any remaining non-latin-1 characters safely.
    """
    if not text:
        return text
    replacements = {
        '\u2022': '-',     # Bullet
        '\u2013': '-',     # En dash
        '\u2014': '--',    # Em dash
        '\u2018': "'",     # Left single quote
        '\u2019': "'",     # Right single quote
        '\u201c': '"',     # Left double quote
        '\u201d': '"',     # Right double quote
        '\u2026': '...',   # Ellipsis
    }
    for unicode_char, ascii_replacement in replacements.items():
        text = text.replace(unicode_char, ascii_replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

def init_dialog():
    d = dialog.Dialog(autowidgetsize=True)
    # Enable interpretation of escape sequences for colors (\Z)
    try:
        d.add_persistent_args(["--colors"])
    except AttributeError:
        # Fallback for old pythondialog versions
        pass
    return d

def multi_select_menu(d, title, options, default_indices=[]):
    """
    Shows a menu with multiple options using d.checklist.
    Installed elements are pre-marked and highlighted.
    """
    choices = []
    for i, opt in enumerate(options):
        tag = str(i + 1)
        item = opt['label']
        is_installed = opt.get('installed', False)
        
        if is_installed:
            item = rf"\Z1{i18n.T('installed_tag')}\Zn {item}"
            status = True
        else:
            status = (i in default_indices)

        choices.append((tag, sanitize_for_dialog(item), status))

    code, selected_tags = d.checklist(sanitize_for_dialog(title), choices=choices, title="refugiOS Installer")
    
    if code == d.OK:
        return [int(tag) - 1 for tag in selected_tags]
    return []

def single_select_menu(d, title, options, default_index):
    """
    Shows a standard menu using d.menu.
    Installed elements are highlighted with a tag.
    """
    choices = []
    for i, opt in enumerate(options):
        item = opt['label']
        if opt.get('installed'):
            item = rf"\Z1{i18n.T('installed_tag')}\Zn {item}"
        choices.append((str(i + 1), sanitize_for_dialog(item)))

    code, tag = d.menu(sanitize_for_dialog(title), choices=choices, title="refugiOS Installer", default_item=str(default_index + 1))

    if code == d.OK:
        return int(tag) - 1
    return None

def simple_question(d, title, prompt_text, default_yes=False):
    """
    Shows an interactive Yes/No question using d.yesno.
    """
    code = d.yesno(sanitize_for_dialog(f"{title}\n\n{prompt_text}"), title="refugiOS Installer",
                   yes_label=i18n.T('yes'), no_label=i18n.T('no'), defaultno=(not default_yes))
    return code == d.OK

# ==============================================================================
# SECTION 4: HIERARCHICAL PACKAGE MANAGEMENT
# ==============================================================================

class TargetEnv:
    """Maintains centrally mapped critical paths where refugiOS will store or read data."""
    def __init__(self, base_dir, desktop_dir):
        self.base = base_dir
        self.desktop = desktop_dir
        self.apps_dir = os.path.join(base_dir, "Apps", "versions")
        self.know_dir = os.path.join(base_dir, "Knowledge", "versions")
        self.ai_dir = os.path.join(base_dir, "AI", "versions")
        self.vault_dir = os.path.join(base_dir, "Vaults")
        self.scripts_dir = os.path.join(base_dir, "Scripts")

def sync_resources(env, sys_info, exec_path):
    """
    Scans version directories, links the best components,
    and ensures desktop launchers exist for everything available.
    """
    log_info(i18n.T('syncing_resources'))
    
    if not os.path.exists(env.know_dir): return

    lang = sys_info.lang
    kiwix_script = os.path.join(env.scripts_dir, 'refugios-kiwix.sh')
    knowledge = os.path.join(env.base, 'Knowledge')
    library_dir = os.path.join(env.desktop, i18n.T('library_folder'))
    valid_launchers = set()

    def write_launcher(path, name, comment, zim_link):
        with open(path, 'w') as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment={comment}
Exec=bash "{kiwix_script}" "{zim_link}"
Icon=accessories-dictionary
Terminal=false
""")
        certify_icon(path)
        valid_launchers.add(path)

    # 1. Wikipedia: only ONE icon, for the highest priority version found
    for w in sorted(WIKIPEDIA_CONFIG, key=lambda x: x.get('priority', 0), reverse=True):
        best = find_local_zim(env.know_dir, w, lang)
        if best:
            link = os.path.join(knowledge, 'wikipedia.zim')
            run_cmd(f"ln -sf '{os.path.join(env.know_dir, best)}' '{link}'", quiet=True)
            write_launcher(os.path.join(env.desktop, "Knowledge_wikipedia.desktop"),
                           "Wikipedia", i18n.T('wikipedia_comment'), link)
            break

    # 2. Rest of the library: the main books on the desktop, the others in a folder
    for entry in LIBRARY_CATALOG:
        best = find_local_zim(env.know_dir, entry, lang)
        if not best:
            continue
        link = os.path.join(knowledge, entry.get('symlink', f"{entry['id']}.zim"))
        run_cmd(f"ln -sf '{os.path.join(env.know_dir, best)}' '{link}'", quiet=True)
        folder = env.desktop if entry.get('desktop') else library_dir
        os.makedirs(folder, exist_ok=True)
        write_launcher(os.path.join(folder, f"Knowledge_{entry['id']}.desktop"),
                       i18n.T(entry['title_key']), i18n.T('generic_zim_comment'), link)

    # 3. Remove obsolete Knowledge icons (old versions, removed resources, or the
    #    library folder of the other language)
    folders = [env.desktop] + [os.path.join(env.desktop, i18n.TRANSLATIONS[l]['library_folder'])
                               for l in i18n.TRANSLATIONS]
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            if fname.startswith('Knowledge_') and fname.endswith('.desktop') and path not in valid_launchers:
                os.remove(path)
                log_info(i18n.T('obsolete_icon').format(fname))
        if folder != env.desktop and not os.listdir(folder):
            os.rmdir(folder)

    # 4. AI Models
    if not os.path.exists(env.ai_dir): return
    for m in AI_MODEL_CONFIG:
        # Exact name only: a prefix match would also pick up the .aria2 control
        # file of an interrupted download, or the .sha256 file next to the model
        target = os.path.join(env.ai_dir, m['filename'])
        if is_download_complete(target):
            run_cmd(f"ln -sf '{target}' '{os.path.join(env.base, 'AI', m['symlink'])}'", quiet=True)

def ensure_dirs(env):
    """Creates project master folder structure on disk if it doesn't exist."""
    log_info(i18n.T('creating_dirs').format(env.base))
    for d in [env.apps_dir, env.know_dir, env.ai_dir, env.vault_dir, env.scripts_dir]:
        os.makedirs(d, exist_ok=True)
    os.makedirs(env.desktop, exist_ok=True)

def install_package(env, name, is_rpi, appimage_url=None, appimage_name=None, flatpak_id=None, apt_deps=None):
    """
    Main deployment engine. Tries to install resources following a cascading behavior
    and priorities, ideal for ensuring universal compatibility in Linux.
    
    PC Hierarchy:
       1) Try AppImage (native portable)
       2) Try Flatpak
       3) Try APT (Debian/Ubuntu)
    
    ARM Hierarchy (Raspberry Pi):
       - Prioritizes APT or internal installation since many AppImages lack ARM binaries.
    """
    log_info(i18n.T('installing_package').format(name))
    
    # Raspberry Pi Special Handling:
    if is_rpi:
        if apt_deps:
            log_info(f"Raspberry Pi Mode: Overriding priorities... Trying native APT install for '{name}'...")
            if run_cmd(f"sudo apt-get install -y {apt_deps}", quiet=True):
                log_success(i18n.T('installed_apt').format(name))
                return True
        log_info(f"No APT packages available for {name}. Skipping or using manual alternative.")
        return False
        
    # PC - Level 1: AppImage
    if appimage_url and appimage_name:
        dest_path = os.path.join(env.apps_dir, appimage_name)
        if not os.path.exists(dest_path):
            log_info(f"Testing AppImage via direct link: {appimage_name}")
            if download_with_aria2(appimage_url, dest_path, timeout=120):
                run_cmd(f"chmod +x '{dest_path}'", quiet=True)
                log_success(i18n.T('installed_appimage').format(name))
                return dest_path
            log_info(f"AppImage download failed for {name}. Trying next method...")
        else:
            run_cmd(f"chmod +x '{dest_path}'", quiet=True)
            log_success(i18n.T('installed_appimage').format(name))
            return dest_path

    # PC - Level 2: Flatpak
    if flatpak_id:
        log_info(f"Jumping to Flatpak repository to resolve {name}...")
        run_cmd("sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo", quiet=True)
        if run_cmd(f"sudo flatpak install flathub {flatpak_id} -y", quiet=True):
            log_success(i18n.T('installed_flatpak').format(name))
            return True
        log_info(f"Flatpak installation failed for {name}. Trying next method...")

    # PC - Level 3: APT
    if apt_deps:
        log_info(f"No portable options. Trying {name} via classic APT repository...")
        if run_cmd(f"sudo apt-get install -y {apt_deps}", quiet=True):
            log_success(i18n.T('installed_recursive_apt').format(name))
            return True
        log_info(f"APT installation failed for {name}.")
            
    log_err(i18n.T('install_failed').format(name), fatal=False)
    return False

# ==============================================================================
# SECTION 5: ADDITIONAL TOOLS (Basic Web Scraping)
# ==============================================================================

FETCH_TIMEOUT = 20

def fetch_url(url):
    """
    Performs a simple HTTP request and returns HTML/Text response.
    Simulates a traditional web browser User-Agent.
    The timeout prevents a mirror that accepts the connection but never answers
    from hanging the whole installer.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
        return resp.read().decode('utf-8')

# ==============================================================================
# SECTION 6: VERIFIED DOWNLOADS, KNOWLEDGE LIBRARY AND MAPS
# ==============================================================================

_LISTING_CACHE = {}

def fetch_listing(url):
    """Directory listing of a mirror, fetched once per run."""
    if url not in _LISTING_CACHE:
        _LISTING_CACHE[url] = fetch_url(url)
    return _LISTING_CACHE[url]

def is_download_complete(path):
    """A file with an aria2 control file next to it is an interrupted download."""
    return os.path.isfile(path) and not os.path.exists(path + ".aria2")

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def sha1_base64_of(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return base64.b64encode(h.digest()).decode()

def write_checksum_file(path, digest):
    """Stores the expected SHA-256 next to the file, so it can be checked offline later."""
    try:
        with open(path + ".sha256", "w") as f:
            f.write(f"{digest}  {os.path.basename(path)}\n")
    except OSError:
        pass

def verify_sha256(path, expected):
    """Hashes the file and compares it; on success records the checksum file."""
    if not expected:
        return True
    log_info(i18n.T('verifying_file').format(os.path.basename(path)))
    if sha256_of(path) != expected.lower():
        return False
    write_checksum_file(path, expected.lower())
    return True

def fetch_kiwix_sha256(file_url):
    """Kiwix publishes '<file>.sha256' next to every ZIM."""
    try:
        m = re.match(r'\s*([0-9a-fA-F]{64})', fetch_url(file_url + ".sha256"))
        return m.group(1).lower() if m else None
    except Exception:
        return None

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def fetch_hf_sha256(file_url):
    """
    Hugging Face answers a 'resolve' URL with a redirect whose X-Linked-Etag
    header is the SHA-256 of the LFS file. The redirect is not followed: the
    CDN it points to does not repeat the header.
    """
    req = urllib.request.Request(file_url, method="HEAD", headers={'User-Agent': 'Mozilla/5.0'})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        headers = opener.open(req, timeout=FETCH_TIMEOUT).headers
    except urllib.error.HTTPError as e:
        headers = e.headers
    except Exception:
        return None
    etag = (headers.get('X-Linked-Etag') or '').strip()
    if etag.startswith('W/'):
        etag = etag[2:]
    etag = etag.strip('"').lower()
    return etag if re.fullmatch(r'[0-9a-f]{64}', etag) else None

def entry_size_mb(entry, lang):
    size = entry.get('size_mb', 0)
    if isinstance(size, dict):
        return size.get(lang, size.get('en', 0))
    return size

def format_size(mb):
    if mb >= 10240:
        text = f"~{round(mb / 1024)} GB"
    elif mb >= 1024:
        text = f"~{mb / 1024:.1f} GB"
    else:
        text = f"~{mb} MB"
    return text.replace('.', ',') if i18n.REFUGIOS_LANG == 'es' else text

def zim_stems(entry, lang):
    """Candidate file stems for a catalog entry, preferred language first."""
    stem = entry['stem']
    if '{lang}' not in stem:
        return [stem]
    stems = [stem.format(lang=lang)]
    if lang != 'en':
        stems.append(stem.format(lang='en'))
    return stems

def zim_regex(stem):
    return re.compile(re.escape(stem) + r'_\d{4}-\d{2}[a-z]?\.zim$')

def zim_language_tag(entry, lang):
    """Marks books that will not be in the user's language."""
    if '{lang}' in entry['stem'] or f"_{lang}_" in entry['stem']:
        return ""
    return f" {i18n.T('lib_english_tag')}"

def catalog_label(entry, lang):
    return f"{i18n.T(entry['label_key'])}{zim_language_tag(entry, lang)} ({format_size(entry_size_mb(entry, lang))})"

def find_local_zim(know_dir, entry, lang):
    """Newest complete local file for a catalog entry, or None."""
    if not os.path.isdir(know_dir):
        return None
    files = os.listdir(know_dir)
    for stem in zim_stems(entry, lang):
        rx = zim_regex(stem)
        matches = sorted(f for f in files
                         if rx.match(f) and is_download_complete(os.path.join(know_dir, f)))
        if matches:
            return matches[-1]
    return None

def find_remote_zim(entry, lang):
    """
    Newest published file for a catalog entry, as (file name, mirrors).
    The mirrors are every listed base URL that carries that exact file.
    """
    listings = []
    for url in entry['urls']:
        try:
            listings.append((url, fetch_listing(url)))
        except Exception:
            continue
    for i, stem in enumerate(zim_stems(entry, lang)):
        if i > 0:
            log_info(i18n.T('zim_fallback').format(lang, entry['id']))
        rx = re.compile(r'href="(' + re.escape(stem) + r'_\d{4}-\d{2}[a-z]?\.zim)"')
        for url, html in listings:
            matches = rx.findall(html)
            if matches:
                name = sorted(matches)[-1]
                mirrors = [url] + [u for u, h in listings if u != url and f'href="{name}"' in h]
                return name, mirrors
    return None, []

def download_zim(know_dir, zim_name, mirrors, prefer_torrent=False):
    """
    Downloads a ZIM trying, in order: the Kiwix metalink (mirror selection and
    piece-by-piece hash checking done by aria2), each mirror directly (checked
    against the published SHA-256 afterwards), and BitTorrent. With
    prefer_torrent the BitTorrent attempt goes first.
    """
    dest = os.path.join(know_dir, zim_name)
    primary = mirrors[0] + zim_name
    expected = fetch_kiwix_sha256(primary)
    common = (f"--continue=true --auto-file-renaming=false --timeout=15 --connect-timeout=10 "
              f"--max-tries=5 --summary-interval=0 --dir=\"{know_dir}\"")

    # A small split size lets aria2 spread even small books over several
    # mirrors, so one slow mirror cannot stall the download
    attempts = [("metalink", f"aria2c -x 8 -s 8 --min-split-size=2M {common} --follow-metalink=mem "
                             f"--metalink-preferred-protocol=https \"{primary}.meta4\"")]
    for m in mirrors:
        attempts.append(("direct", f"aria2c -x 8 -s 8 {common} -o \"{zim_name}\" \"{m}{zim_name}\""))
    torrent = ("torrent", f"aria2c --seed-time=0 {common} --follow-torrent=mem \"{primary}.torrent\"")
    if prefer_torrent:
        attempts.insert(0, torrent)
    else:
        attempts.append(torrent)

    previous = None
    for method, cmd in attempts:
        # A control file left by a different method cannot be trusted: drop it
        # and let aria2 re-check what is already on disk instead.
        if previous and previous != method and os.path.exists(dest):
            try:
                os.remove(dest + ".aria2")
            except OSError:
                pass
            if method != "direct":
                cmd += " --check-integrity=true"
        previous = method
        log_info(i18n.T('zim_download_method').format(method, zim_name))
        if not run_cmd(cmd) or not is_download_complete(dest):
            continue
        if method == "direct" and expected:
            if not verify_sha256(dest, expected):
                log_info(i18n.T('checksum_mismatch').format(zim_name))
                os.remove(dest)
                continue
        elif expected:
            write_checksum_file(dest, expected)
        return True
    return False

def install_zim(env, entry, lang, force_dl, prefer_torrent):
    """Resolves, downloads and verifies one catalog entry. Never fatal."""
    log_info(i18n.T('tracking_zim').format(entry['id'], entry['stem'].format(lang=lang)))
    zim_name, mirrors = find_remote_zim(entry, lang)
    if not zim_name:
        log_err(i18n.T('zim_not_found').format(entry['id'], entry['stem'], lang), fatal=False)
        return False
    target = os.path.join(env.know_dir, zim_name)
    if is_download_complete(target) and not force_dl:
        log_info(i18n.T('zim_exists').format(zim_name))
        return True
    if force_dl and is_download_complete(target):
        os.remove(target)
    log_info(i18n.T('downloading_zim').format(zim_name))
    if download_zim(env.know_dir, zim_name, mirrors, prefer_torrent):
        log_success(i18n.T('zim_verified').format(zim_name))
        return True
    log_err(i18n.T('zim_all_methods_failed').format(zim_name), fatal=False)
    return False

WIKI_SPACE_SHARE = 0.35
BOOK_SPACE_SHARE = 0.10

def default_wiki_index(free_space_mb, lang):
    """Menu index of the largest Wikipedia taking at most WIKI_SPACE_SHARE of the free space."""
    best = 1
    for i, c in enumerate(WIKIPEDIA_CONFIG, 1):
        if entry_size_mb(c, lang) <= free_space_mb * WIKI_SPACE_SHARE:
            best = i
    return best

def visible_catalog(lang):
    return [e for e in LIBRARY_CATALOG if lang in e.get('only_langs', [lang])]

def organic_maps_data_dir():
    """Writable data dir of the Organic Maps Flatpak (renamed in newer releases)."""
    base = os.path.join(os.path.expanduser("~"), ".var", "app", ORGANIC_MAPS_ID, "data")
    newer = os.path.join(base, "OrganicMaps")
    return newer if os.path.isdir(newer) else os.path.join(base, "OMaps")

def organic_maps_countries():
    """
    countries.txt bundled with the installed app. Its "v" is the map data
    version the app expects, and its tree lists every region with size and hash.
    """
    candidates = []
    location = get_cmd_output(f"flatpak info --show-location {ORGANIC_MAPS_ID} 2>/dev/null")
    if location:
        candidates.append(os.path.join(location, "files", "share", "organicmaps", "data", "countries.txt"))
    candidates.append("/usr/share/organicmaps/data/countries.txt")
    for path in candidates:
        try:
            with open(path, encoding="utf-8") as f:
                tree = json.load(f)
            if tree.get('v') and tree.get('g'):
                return tree
        except (OSError, ValueError):
            continue
    return None

def map_leaves(node):
    if not node.get('g'):
        return [node]
    leaves = []
    for child in node['g']:
        leaves += map_leaves(child)
    return leaves

def map_regions_for(presets, tree):
    """Every downloadable region under the countries of the chosen presets, without repeats."""
    by_id = {c['id']: c for c in tree.get('g', [])}
    regions = {}
    for preset in presets:
        for country in preset['countries']:
            node = by_id.get(country)
            if node is None:
                log_info(i18n.T('map_country_missing').format(country))
                continue
            for leaf in map_leaves(node):
                regions[leaf['id']] = leaf
    return list(regions.values())

def organic_maps_servers():
    try:
        servers = json.loads(fetch_url(ORGANIC_MAPS_META))
        if isinstance(servers, list) and servers:
            return servers + [s for s in ORGANIC_MAPS_FALLBACK_SERVERS if s not in servers]
    except Exception:
        pass
    return list(ORGANIC_MAPS_FALLBACK_SERVERS)

def map_region_ok(path, leaf):
    if not is_download_complete(path):
        return False
    if leaf.get('s') and os.path.getsize(path) != leaf['s']:
        return False
    return not leaf.get('sha1_base64') or sha1_base64_of(path) == leaf['sha1_base64']

def install_map_regions(presets):
    """
    Downloads the regions of the chosen presets straight into the folder where
    Organic Maps looks for them, for the data version the installed app
    expects, checking each file against the size and SHA-1 the app itself uses.
    """
    tree = organic_maps_countries()
    if tree is None:
        log_err(i18n.T('maps_data_missing'), fatal=False)
        return False
    version = str(tree['v'])
    dest_dir = os.path.join(organic_maps_data_dir(), version)
    os.makedirs(dest_dir, exist_ok=True)
    regions = map_regions_for(presets, tree)
    servers = organic_maps_servers()
    failed = []
    for i, leaf in enumerate(regions, 1):
        name = leaf['id'] + ".mwm"
        dest = os.path.join(dest_dir, name)
        if map_region_ok(dest, leaf):
            continue
        log_info(i18n.T('map_downloading').format(i, len(regions), leaf['id']))
        ok = False
        for server in servers:
            url = f"{server.rstrip('/')}/maps/{version}/{urllib.parse.quote(name)}"
            if download_with_aria2(url, dest, timeout=3600) and map_region_ok(dest, leaf):
                ok = True
                break
            if is_download_complete(dest):
                os.remove(dest)
        if not ok:
            failed.append(leaf['id'])
    if failed:
        log_err(i18n.T('maps_regions_failed').format(len(failed), ", ".join(failed[:8])), fatal=False)
        return False
    log_success(i18n.T('maps_regions_ok').format(len(regions)))
    return True

# ==============================================================================
# MASTER BLOCK: GENERAL CONTROLLER (main)
# ==============================================================================
def main():
    # Initial safeguard for local permissions.
    if os.geteuid() == 0:
        log_err("Operation blocked. This installer script should not be run as root. Run it as your regular user and it will use 'sudo' only where internally needed.")

    # 0. Initialize Dialog
    d = init_dialog()

    # 1. System Information Retrieval
    sys_info = SystemInfo()
    
    # 2. Language Selection (Persistent)
    lang_options = [
        {"label": "English", "code": "en"},
        {"label": "Español", "code": "es"}
    ]
    # Find index of current detected language
    default_lang_idx = 0
    for i, opt in enumerate(lang_options):
        if opt['code'] == sys_info.lang:
            default_lang_idx = i
            break
            
    selected_lang_idx = single_select_menu(d, i18n.T('lang_config_title'), lang_options, default_lang_idx)
    if selected_lang_idx is not None:
        new_lang = lang_options[selected_lang_idx]['code']
        sys_info.lang = new_lang
        i18n.save_lang(new_lang)
    
    # Diagnosis display
    diag_info = f"""{i18n.T('os_label')}: {sys_info.os_type}
"""
    if sys_info.rpi_model:
        diag_info += f"{i18n.T('rpi_model_label')}: {sys_info.rpi_model}\n"
    
    diag_info += f"""{i18n.T('desktop_env_label')}: {sys_info.desktop_env}
{i18n.T('ram_label')}: {sys_info.ram_mb} MB
{i18n.T('disk_space_label')}: {sys_info.free_space_mb} MB
{i18n.T('gpu_label')}: {sys_info.gpu_info}
{i18n.T('vram_label')}: {sys_info.vram_info}
{i18n.T('detected_lang_label')}: {sys_info.lang}
"""
    if sys_info.is_rpi:
        diag_info += f"\n{i18n.T('rpi_arch_detected')}"
    elif sys_info.has_nvidia:
        diag_info += f"\n{i18n.T('nvidia_detected_note')}"

    d.msgbox(sanitize_for_dialog(diag_info), title=i18n.T('sys_diag_title'))

    # Depending on disk space, offer lightweight or enriched configurations
    if sys_info.free_space_mb < 30000:
        log_info(i18n.T('lite_mode_msg'))
        storage_mode = "lite"
    elif sys_info.free_space_mb < 70000:
        log_info(i18n.T('standard_mode_msg'))
        storage_mode = "standard"
    else:
        log_info(i18n.T('rich_mode_msg'))
        storage_mode = "rich"

    # Preselect the largest Wikipedia that leaves room for everything else. Sizes
    # differ a lot between languages (the full English one is over 100 GB), so a
    # fixed tier per storage mode would not fit. Index 0 of the menu is "skip".
    def_wiki = default_wiki_index(sys_info.free_space_mb, sys_info.lang)

    # Preselect AI models considering both disk space and available system RAM.
    # Models >= 8GB (ia_base, ia_med) require at least 6-8GB of physical RAM.
    if sys_info.ram_mb < 6000 or sys_info.free_space_mb < 30000:
        def_ai = [0]
    elif sys_info.free_space_mb < 70000 or sys_info.ram_mb < 12000:
        def_ai = [0, 1]
    else:
        def_ai = [1, 2, 3]

    # Force download mode
    force_dl = simple_question(d, i18n.T('rewrite_mode_title'), i18n.T('rewrite_mode_prompt'), default_yes=False)

    # ==========================
    # INSTALLED COMPONENT DETECTION
    # ==========================
    home_dir = os.environ['HOME']
    base_dir = os.path.join(home_dir, "refugiOS")
    desktop_dir = os.path.join(home_dir, "Desktop")
    if not os.path.isdir(desktop_dir):
        desktop_dir = os.path.join(home_dir, "Escritorio")
    
    env = TargetEnv(base_dir, desktop_dir)
    lang = sys_info.lang

    # Wikipedia versions
    wiki_opts = [{"label": i18n.T('wiki_skip_label'), "skip": True}]
    for c in WIKIPEDIA_CONFIG:
        opt = {"label": catalog_label(c, lang), "entry": c}
        if find_local_zim(env.know_dir, c, lang):
            opt['installed'] = True
        wiki_opts.append(opt)

    # Rest of the library, one checklist per group
    library_menus = []
    for group in LIBRARY_GROUPS:
        entries = [e for e in visible_catalog(lang) if e['group'] == group['id']]
        opts = []
        defaults = []
        for i, e in enumerate(entries):
            opt = {"label": catalog_label(e, lang), "entry": e}
            if find_local_zim(env.know_dir, e, lang):
                opt['installed'] = True
            # A preset never preselects a book that would take a large share of
            # the disk: sizes vary a lot between languages
            if (storage_mode in e.get('presets', [])
                    and entry_size_mb(e, lang) <= sys_info.free_space_mb * BOOK_SPACE_SHARE):
                defaults.append(i)
            opts.append(opt)
        library_menus.append((group, opts, defaults))

    # AI Models
    ai_opts = []
    for m in AI_MODEL_CONFIG:
        opt = {
            "label": i18n.T(m['label_key']),
            "filename": m['filename'],
            "url": m['url'],
            "symlink": m['symlink'],
            "id": m['id'],
            "size_mb": m.get('size_mb', 0)
        }
        if is_download_complete(os.path.join(env.ai_dir, m['filename'])):
            opt['installed'] = True
        ai_opts.append(opt)

    # ==========================
    # INSTALLER QUESTIONNAIRES
    # ==========================

    wiki_selected = single_select_menu(d, i18n.T('wiki_menu_title'), wiki_opts, def_wiki)

    library_selected = []
    for group, opts, defaults in library_menus:
        if not opts:
            continue
        for idx in multi_select_menu(d, i18n.T(group['title_key']), opts, defaults):
            library_selected.append(opts[idx])

    install_maps = simple_question(d, i18n.T('maps_menu_title'), i18n.T('maps_menu_prompt'), default_yes=True)

    maps_selected = []
    if install_maps:
        map_opts = [{"label": f"{i18n.T(p['label_key'])} ({format_size(p['size_mb'])})", "preset": p}
                    for p in MAP_PRESETS]
        default_map = [0] if lang == 'es' else []
        maps_selected = [map_opts[i]['preset'] for i in
                         multi_select_menu(d, i18n.T('maps_regions_title'), map_opts, default_map)]

    install_extras = simple_question(d, i18n.T('extras_menu_title'), i18n.T('extras_menu_prompt'), default_yes=True)

    translator_installed = subprocess.call(f"flatpak info {TRANSLATOR_ID} >/dev/null 2>&1", shell=True) == 0
    install_translator = simple_question(d, i18n.T('translator_menu_title'), i18n.T('translator_menu_prompt'),
                                         default_yes=sys_info.free_space_mb >= 30000 or translator_installed)

    ai_selected = multi_select_menu(d, i18n.T('ia_menu_title'), ai_opts, def_ai)

    install_nvidia = False
    if sys_info.has_nvidia and not sys_info.is_rpi:
        install_nvidia = simple_question(
            d,
            i18n.T('nvidia_title'),
            i18n.T('nvidia_prompt').format(sys_info.gpu_info),
            default_yes=True
        )

    use_torrent = simple_question(d, i18n.T('p2p_menu_title'), i18n.T('p2p_menu_prompt'), default_yes=False)
    
    estimated_mb = 300
    if install_extras:
        estimated_mb += 1300
    if install_nvidia:
        estimated_mb += 1200
    estimated_mb += 160

    if wiki_selected is not None and wiki_selected > 0:
        opt = wiki_opts[wiki_selected]
        if not opt.get('installed'):
            estimated_mb += entry_size_mb(opt['entry'], lang)

    for opt in library_selected:
        if not opt.get('installed'):
            estimated_mb += entry_size_mb(opt['entry'], lang)

    if install_maps:
        if not shutil.which("flatpak") or subprocess.call(f"flatpak info {ORGANIC_MAPS_ID} >/dev/null 2>&1", shell=True) != 0:
            estimated_mb += 2100
        estimated_mb += sum(p['size_mb'] for p in maps_selected)

    if install_translator and not translator_installed:
        estimated_mb += TRANSLATOR_SIZE_MB

    if ai_selected:
        if not os.path.exists(os.path.join(env.ai_dir, 'llamafile')):
            estimated_mb += 300
        for idx in ai_selected:
            opt = ai_opts[idx]
            if not opt.get('installed'):
                estimated_mb += opt.get('size_mb', 0)

    estimated_gb = round(estimated_mb / 1024, 2)
    warning_msg = ""
    if sys_info.free_space_mb < estimated_mb * 1.2:
        free_gb = round(sys_info.free_space_mb / 1024, 2)
        warning_msg = i18n.T('space_warning_msg').format(free_gb, estimated_gb)

    confirm_text = f"{i18n.T('confirm_install_prompt')}\n\n{i18n.T('estimated_space_msg').format(estimated_gb)}{warning_msg}"
    
    if not simple_question(d, i18n.T('confirm_install_title'), confirm_text, default_yes=True):
        log_err(i18n.T('install_aborted'))

    if os.environ.get("DEBUG") == "1":
        print(f"\n\033[1;33m[!] {i18n.T('warning')}:\033[0m {i18n.T('debug_simulation')}")
        sys.exit(0)

    # =========================================================
    # PHYSICAL EXECUTION AND INSTALLATION
    # =========================================================

    d.msgbox(sanitize_for_dialog(i18n.T('install_starting_msg')), title=i18n.T('install_starting_title'))
    os.system('clear')

    size_logger = SizeLogger()

    ensure_dirs(env)
    cleanup_obsolete_icons(env.desktop)

    # Phase 1: OS Utilities Deployment
    log_info(i18n.T('fixing_perms'))
    run_cmd("sudo systemctl stop unattended-upgrades 2>/dev/null || true", quiet=True)
    run_cmd("sudo dpkg --configure -a", quiet=True)
    run_cmd("sudo apt-get install -f -y", quiet=True)
    run_cmd("sudo apt-get update", quiet=True)

    log_info(i18n.T('installing_base_deps'))
    
    base_pkgs = [
        "python3", "python3-dialog", "dialog", "aria2", "pciutils",
        "curl", "bash", "jq", "rsync", "apt-utils", "flatpak",
        "cryptsetup", "epiphany-browser", "gedit", "xfce4-terminal",
        "dbus-user-session", "xdg-desktop-portal", "libglib2.0-bin",
        "libfuse2t64",
        "language-selector-common",
    ]
    if install_extras:
        log_info(i18n.T('adding_extras'))
        base_pkgs += ["syncthing", "libreoffice", "vlc", "evince"]

    for pkg in base_pkgs:
        run_cmd(f"sudo apt-get install -y {pkg}", quiet=True)

    log_info(i18n.T('syncing_lang_pkgs').format(sys_info.lang))
    if shutil.which("check-language-support"):
        run_cmd(f"check-language-support -l {sys_info.lang} 2>/dev/null | xargs sudo apt-get install -y", quiet=True)
    else:
        run_cmd(f"sudo apt-get install -y hunspell-{sys_info.lang} hyphen-{sys_info.lang} 2>/dev/null || true", quiet=True)
    # check-language-support only exists on Ubuntu, and package names differ
    # between languages: install the dictionaries explicitly
    if sys_info.lang in SPELLING_PACKAGES:
        run_cmd(f"sudo apt-get install -y {SPELLING_PACKAGES[sys_info.lang]}", quiet=True)

    # System compatibility patches
    fix_flatpak_permissions()
    if sys_info.is_rpi:
        fix_rpi_pcmanfm_warnings()

    if install_nvidia:
        log_info(i18n.T('installing_nvidia_driver'))
        install_package(
            env, "NVIDIA Proprietary Driver", sys_info.is_rpi,
            appimage_url=None, appimage_name=None, flatpak_id=None,
            apt_deps="nvidia-driver firmware-misc-nonfree"
        )

    size_logger.log_section("Fase 1: OS Utilities & Ofimática")

    # Phase 2: Install Kiwix Visual Interface
    kiwix_appimage_url = None
    kiwix_appimage_name = None
    try:
        html = fetch_url("https://download.kiwix.org/release/kiwix-desktop/")
        matches = re.findall(r'href="(kiwix-desktop_x86_64_[0-9.-]*\.appimage)"', html)
        if matches:
            kiwix_appimage_name = sorted(matches, key=version_key)[-1]
            kiwix_appimage_url = f"https://download.kiwix.org/release/kiwix-desktop/{kiwix_appimage_name}"
    except Exception as e:
        print(f"\033[1;33m[!] {i18n.T('warning')}:\033[0m Error fetching Kiwix AppImage: {e}")

    # Recent Kiwix AppImages need a newer glibc than Debian 11 and similar
    # distributions have (issue #10): there, go straight to the Flatpak
    glibc = glibc_version()
    if kiwix_appimage_url and glibc and glibc < KIWIX_APPIMAGE_MIN_GLIBC:
        log_info(i18n.T('kiwix_old_glibc').format(".".join(map(str, glibc))))
        kiwix_appimage_url = None

    kiwix_path = install_package(env, "Knowledge Library (Kiwix Desktop)", sys_info.is_rpi, 
        appimage_url=kiwix_appimage_url, 
        appimage_name=kiwix_appimage_name, 
        flatpak_id="org.kiwix.desktop", 
        apt_deps="kiwix")

    if isinstance(kiwix_path, str) and kiwix_path.endswith('.appimage'):
        run_cmd(f"ln -sf '{kiwix_path}' '{os.path.join(env.apps_dir, '../kiwix-desktop.appimage')}'")
        exec_path = os.path.join(env.base, "Apps", "kiwix-desktop.appimage")
    else:
        exec_path = "/usr/bin/kiwix-desktop" if sys_info.is_rpi else "kiwix-desktop"

    size_logger.log_section("Fase 2: Kiwix Desktop")

    # Phase 3: Knowledge Bases (ZIM)
    log_info(i18n.T('scanning_zim'))

    # 3a: Wikipedia (single selected version, or skip)
    if wiki_selected is not None and wiki_selected > 0:
        install_zim(env, wiki_opts[wiki_selected]['entry'], lang, force_dl, use_torrent)

    # 3b: Rest of the library
    for opt in library_selected:
        install_zim(env, opt['entry'], lang, force_dl, use_torrent)

    size_logger.log_section("Fase 3: Bases de Conocimiento (ZIM)")

    # Phase 4: Optional Cartographic Deployment (Organic Maps)
    repo_url = os.environ.get("REPO_URL", "https://raw.githubusercontent.com/Ganso/refugiOS/main")
    
    def fetch_script(s_name):
        d_path = os.path.join(env.scripts_dir, s_name)
        local_dir = os.path.dirname(os.path.realpath(__file__))
        local_s = os.path.join(local_dir, "scripts", s_name)

        # Developer Mode: running from a checkout of the repository, the local scripts
        # take precedence. Otherwise the published version would silently replace them
        # and local changes could never be tested (same reasoning as install.sh).
        if os.path.exists(local_s):
            shutil.copy(local_s, d_path)
            os.chmod(d_path, 0o755)
            return d_path

        # Force download latest version with cache busting
        nocache = random.randint(1000, 9999)
        ok = download_with_aria2(f"{repo_url}/scripts/{s_name}?{nocache}", d_path, timeout=30, keep_partial=False)
        if not ok or not os.path.exists(d_path) or os.path.getsize(d_path) == 0:
            log_err(i18n.T('script_not_found').format(s_name), fatal=False)
            return None
        if os.path.exists(d_path):
            os.chmod(d_path, 0o755)
        return d_path if os.path.exists(d_path) else None

    if install_maps:
        install_package(env, "Offline GPS Maps (Organic Maps)", sys_info.is_rpi, flatpak_id="app.organicmaps.desktop")
        
        if sys_info.is_rpi:
            run_cmd("sudo flatpak override --device=dri app.organicmaps.desktop", quiet=True)

        if maps_selected:
            install_map_regions(maps_selected)
        
        maps_script = fetch_script("refugios-maps.sh")
        if maps_script is None:
            log_err(i18n.T('script_not_found').format("refugios-maps.sh"), fatal=False)
        else:
            maps_desktop = os.path.join(env.desktop, "Offline_Maps.desktop")
            with open(maps_desktop, "w") as f:
                f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={i18n.T('maps_gps_name')}
Exec=bash "{maps_script}"
Icon=app.organicmaps.desktop
Terminal=false
""")
            certify_icon(maps_desktop)
    else:
        log_info(i18n.T('skip_maps_log'))

    size_logger.log_section("Fase 4: Mapas Offline (Organic Maps)")

    # Phase 4b: Offline translator
    if install_translator:
        if install_package(env, "Offline Translator (LocalTranslate)", sys_info.is_rpi, flatpak_id=TRANSLATOR_ID):
            translator_desktop = os.path.join(env.desktop, "Translator.desktop")
            with open(translator_desktop, "w") as f:
                f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={i18n.T('translator_desktop_name')}
Comment={i18n.T('translator_desktop_comment')}
Exec=flatpak run {TRANSLATOR_ID}
Icon={TRANSLATOR_ID}
Terminal=false
""")
            certify_icon(translator_desktop)
        size_logger.log_section("Fase 4b: Traductor offline")

    # Phase 5: AI Motor (Llamafile)
    script_path = fetch_script("refugios-ai-selector.sh")
    if ai_selected:
        log_info(i18n.T('installing_ai_engine_log'))
        try:
             req = urllib.request.Request("https://api.github.com/repos/Mozilla-Ocho/llamafile/releases/latest")
             with urllib.request.urlopen(req) as r:
                  release_data = json.loads(r.read().decode())
             llama_url = None
             for asset in release_data.get('assets', []):
                  if re.match(r'llamafile-[0-9.]+$', asset['name']):
                       llama_url = asset['browser_download_url']
                       llama_name = asset['name']
                       break
             if llama_url:
                  l_path = os.path.join(env.ai_dir, llama_name)
                  if not os.path.exists(l_path) or force_dl:
                       download_with_aria2(llama_url, l_path, timeout=120)
                  os.chmod(l_path, 0o755)
                  run_cmd(f"ln -sf '{l_path}' '{os.path.join(env.base, 'AI', 'llamafile')}'")
        except:
              log_err("Error connecting to GitHub for Llamafile.", fatal=False)

        for idx in ai_selected:
            opt = ai_opts[idx]
            full_url = opt['url']
            m_path = os.path.join(env.ai_dir, opt['filename'])
            if force_dl and is_download_complete(m_path):
                os.remove(m_path)
            if not is_download_complete(m_path):
                log_info(i18n.T('downloading_model').format(opt['filename']))
                expected = fetch_hf_sha256(full_url)
                if not download_with_aria2(full_url, m_path, timeout=300):
                    log_err(i18n.T('model_download_failed').format(opt['filename']), fatal=False)
                    continue
                if not verify_sha256(m_path, expected):
                    log_err(i18n.T('checksum_mismatch').format(opt['filename']), fatal=False)
                    os.remove(m_path)
                    continue
            run_cmd(f"ln -sf '{m_path}' '{os.path.join(env.base, 'AI', opt['symlink'])}'")

        ai_assist_desktop = os.path.join(env.desktop, "AI_Assistant.desktop")
        if script_path is None or not os.path.isfile(script_path):
            err_msg = i18n.T('ai_script_missing')
            log_err(err_msg, fatal=False)
            try:
                d.msgbox(sanitize_for_dialog(err_msg), title=i18n.T('warning'))
                os.system('clear')
            except Exception:
                pass
        else:
            with open(ai_assist_desktop, "w") as f:
                 f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={i18n.T('ai_desktop_name')}
Comment={i18n.T('ai_desktop_desc')}
Exec=xfce4-terminal -e "{script_path}"
Icon=utilities-terminal
Terminal=false
""")
            certify_icon(ai_assist_desktop)

    size_logger.log_section("Fase 5: Motor AI y Modelos")

    # Phase 6: Privacy Cryptographic Foundations
    log_info(i18n.T('installing_vaults_log'))
    
    vault_script = fetch_script("refugios-vault.py")

    # Pre-validation: verify the vault script actually exists on disk before
    # attempting to reference or execute it. Warns the user (descriptive log +
    # dialog notice) and skips the vault desktop icon, but does NOT halt the
    # overall installation so the rest of the modules can still be deployed.
    vault_script_ok = bool(vault_script) and os.path.isfile(vault_script)
    if not vault_script_ok:
        err_msg = i18n.T('vault_script_missing')
        log_err(err_msg, fatal=False)
        try:
            d.msgbox(sanitize_for_dialog(err_msg), title=i18n.T('warning'))
            os.system('clear')
        except Exception:
            pass

    i18n_src = os.path.join(os.path.dirname(os.path.realpath(__file__)), "i18n.py")
    i18n_dst = os.path.join(env.scripts_dir, "i18n.py")
    if os.path.exists(i18n_src):
        shutil.copy(i18n_src, i18n_dst)

    if vault_script_ok:
        vault_desktop = os.path.join(env.desktop, "Vault_Manager.desktop")
        with open(vault_desktop, "w") as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={i18n.T('vault_title')}
Comment={i18n.T('vault_manager_comment')}
Exec=xfce4-terminal -e "python3 {vault_script}"
Icon=dialog-password
Terminal=false
""")
        certify_icon(vault_desktop)

    ensure_install_icon(env, sys_info)

    # Offline self-check of everything installed (books, AI, maps, vaults)
    check_script = fetch_script("refugios-check.py")
    if check_script and os.path.isfile(check_script):
        check_desktop = os.path.join(env.desktop, "Check_refugiOS.desktop")
        with open(check_desktop, "w") as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={i18n.T('check_desktop_name')}
Comment={i18n.T('check_desktop_comment')}
Exec=xfce4-terminal -e "python3 {check_script}"
Icon=emblem-default
Terminal=false
""")
        certify_icon(check_desktop)
    else:
        log_err(i18n.T('check_script_missing'), fatal=False)

    size_logger.log_section("Fase 6: Bóveda de Seguridad")


    # PCManFM Quick execution hack (typical for Raspberry Pi OS)
    # Ensuring quick_exec=1 to avoid prompting on script launch
    libfm_conf = os.path.join(home_dir, ".config", "libfm", "libfm.conf")
    if os.path.exists(libfm_conf):
        run_cmd(f"sed -i 's/quick_exec=0/quick_exec=1/' '{libfm_conf}'", quiet=True)
        if 'quick_exec=1' not in open(libfm_conf).read():
            run_cmd(f"echo -e '\\n[General]\\nquick_exec=1' >> '{libfm_conf}'", quiet=True)
    else:
        os.makedirs(os.path.dirname(libfm_conf), exist_ok=True)
        with open(libfm_conf, 'w') as f:
            f.write('[General]\nquick_exec=1\n')

    # Ensure intermediate scripts exist
    kiwix_script_path = fetch_script("refugios-kiwix.sh")
    if not kiwix_script_path or not os.path.isfile(kiwix_script_path):
        err_msg = i18n.T('kiwix_script_missing')
        log_err(err_msg, fatal=False)
        try:
            d.msgbox(sanitize_for_dialog(err_msg), title=i18n.T('warning'))
            os.system('clear')
        except Exception:
            pass
    
    # Final resource synchronization
    if 'exec_path' not in locals():
         exec_path = "kiwix-desktop"
    sync_resources(env, sys_info, exec_path)

    # Set desktop background
    set_wallpaper(sys_info)

    # Certify all desktop icons one final time and refresh desktop
    certify_all_desktop_icons(env.desktop)

    total_mb = size_logger.log_total()

    if FAILED_ITEMS:
        log_err(i18n.T('install_errors_summary'), fatal=False)
        report = f"{i18n.T('install_errors_found')}\n\n"
        for item in FAILED_ITEMS:
            report += f" - {item}\n"
        d.msgbox(sanitize_for_dialog(report), title=i18n.T('warning'))
        # Report the failure to the caller (the desktop wrapper logs the exit code)
        sys.exit(1)
    else:
        log_success("GLOBAL DEPLOYMENT OPERATION FINISHED. Please check desktop icon integrity and accessibility.")
        final_msg = f"{i18n.T('install_finished_msg')}\n\n{i18n.T('install_space_used').format(total_mb)}"
        d.msgbox(sanitize_for_dialog(final_msg), title=i18n.T('install_finished_title'))


if __name__ == "__main__":
    main()
