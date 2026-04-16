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
import json
import shutil
import re
import time

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
KNOWLEDGE_CONFIG = [
    {
        "id": "wiki_lite",
        "name": "wikipedia",
        "label": i18n.T('wiki_lite_label'),
        "type": "top_mini",
        "search_url": "https://download.kiwix.org/zim/wikipedia/",
        "priority": 1
    },
    {
        "id": "wiki_total",
        "name": "wikipedia",
        "label": i18n.T('wiki_total_label'),
        "type": "all_nopic",
        "search_url": "https://download.kiwix.org/zim/wikipedia/",
        "priority": 2
    },
    {
        "id": "wikimed",
        "name": "wikimed",
        "label": i18n.T('wikimed_label'),
        "type": "maxi",
        "search_url": "https://download.kiwix.org/zim/wikipedia/",
        "symlink": "wikimed.zim"
    },
    {
        "id": "wikihow",
        "name": "wikihow",
        "label": i18n.T('wikihow_label'),
        "type": "maxi",
        "search_url": "https://mirrors.dotsrc.org/kiwix/archive/zim/wikihow/",
        "symlink": "wikihow.zim"
    }
]

# Artificial Intelligence Models (GGUF)
AI_MODEL_CONFIG = [
    {
        "id": "ia_min",
        "label": i18n.T('ia_min_label'),
        "filename": "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
        "url_base": "https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/",
        "symlink": "minimal-model.gguf"
    },
    {
        "id": "ia_base",
        "label": i18n.T('ia_base_label'),
        "filename": "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf",
        "url_base": "https://huggingface.co/bartowski/microsoft_Phi-4-mini-instruct-GGUF/resolve/main/",
        "symlink": "basic-model.gguf"
    },
    {
        "id": "ia_med",
        "label": i18n.T('ia_med_label'),
        "filename": "Qwen_Qwen3-8B-Q4_K_M.gguf",
        "url_base": "https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF/resolve/main/",
        "symlink": "intermediate-model.gguf"
    },
    {
        "id": "ia_max",
        "label": i18n.T('ia_max_label'),
        "filename": "Qwen_Qwen3-14B-Q4_K_M.gguf",
        "url_base": "https://huggingface.co/bartowski/Qwen_Qwen3-14B-GGUF/resolve/main/",
        "symlink": "advanced-model.gguf"
    }
]

# ==============================================================================
# SECTION 1: UTILITY FUNCTIONS AND LOGS
# ==============================================================================

def log_info(msg):
    """Displays an informative message in blue."""
    print(f"\033[1;34m[*]\033[0m {msg}")

def log_err(msg):
    """Displays a critical error message in red and terminates execution."""
    print(f"\033[1;31m[X] {i18n.T('error')}:\033[0m {msg}")
    sys.exit(1)

def log_success(msg):
    """Displays a success message in green."""
    print(f"\033[1;32m[v] {i18n.T('success')}:\033[0m {msg}")

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
        # Detect if running old graphics server (X11) or modern (Wayland)
        self.desktop_env = os.environ.get("XDG_SESSION_TYPE", "Unknown").capitalize()
        self.ram_mb = 0
        self.free_space_mb = 0
        self.gpu_info = "Unknown"
        self.vram_info = "Unknown"
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
            item += rf" \Z1{i18n.T('installed_tag')}\Zn"
            status = True
        else:
            status = (i in default_indices)
            
        choices.append((tag, item, status))
    
    code, selected_tags = d.checklist(title, choices=choices, title="refugiOS Installer")
    
    if code == d.OK:
        return [int(tag) - 1 for tag in selected_tags]
    return []

def single_select_menu(d, title, options, default_index):
    """
    Shows a standard menu using d.menu.
    """
    choices = []
    for i, opt in enumerate(options):
        choices.append((str(i + 1), opt['label']))
    
    code, tag = d.menu(title, choices=choices, title="refugiOS Installer", default_item=str(default_index + 1))
    
    if code == d.OK:
        return int(tag) - 1
    return None

def simple_question(d, title, prompt_text, default_yes=False):
    """
    Shows an interactive Yes/No question using d.yesno.
    """
    code = d.yesno(f"{title}\n\n{prompt_text}", title="refugiOS Installer", 
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

    # 1. Wikipedia (Choosing the highest priority version found)
    wikis = sorted([c for c in KNOWLEDGE_CONFIG if c['name'] == 'wikipedia'], key=lambda x: x.get('priority', 0), reverse=True)
    for w in wikis:
        regex = rf"wikipedia_{sys_info.lang}_{w['type']}_[0-9-]*\.zim"
        matches = [f for f in os.listdir(env.know_dir) if re.match(regex, f)]
        if matches:
            best_wiki_file = sorted(matches)[-1]
            target = os.path.join(env.know_dir, best_wiki_file)
            run_cmd(f"ln -sf '{target}' '{os.path.join(env.base, 'Knowledge', 'wikipedia.zim')}'", quiet=True)
            break
    
    # 2. Other ZIMs (WikiMed, WikiHow...)
    for c in KNOWLEDGE_CONFIG:
        if not c.get('symlink'): continue
        prefix = "wikipedia" if c['name'] == 'wikimed' else c['name']
        m_name = "_medicine" if c['name'] == 'wikimed' else ""
        regex = rf"{prefix}_{sys_info.lang}{m_name}_{c['type']}_[0-9-]*\.zim"
        
        matches = [f for f in os.listdir(env.know_dir) if re.match(regex, f)]
        if matches:
            best = sorted(matches)[-1]
            target = os.path.join(env.know_dir, best)
            run_cmd(f"ln -sf '{target}' '{os.path.join(env.base, 'Knowledge', c['symlink'])}'", quiet=True)

    # 3. Launchers for Knowledge Bases
    kiwix_script = os.path.join(env.scripts_dir, 'refugios-kiwix.sh')
    valid_kb_desktops = set()  # Names of valid .desktop files that should exist

    # Wikipedia: only ONE icon for the best available version
    wiki_sym_path = os.path.join(env.base, 'Knowledge', 'wikipedia.zim')
    if os.path.exists(wiki_sym_path):
        desktop_name = "Knowledge_wikipedia.desktop"
        valid_kb_desktops.add(desktop_name)
        desktop_file = os.path.join(env.desktop, desktop_name)
        with open(desktop_file, 'w') as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Wikipedia
Comment={i18n.T('wikipedia_comment')}
Exec=bash "{kiwix_script}" "{wiki_sym_path}"
Icon=accessories-dictionary
Terminal=false
""")
        os.chmod(desktop_file, 0o755)

    # Rest of ZIMs (WikiMed, WikiHow): one icon per resource
    for c in KNOWLEDGE_CONFIG:
        if c['name'] == 'wikipedia': continue  # Already treated above
        if not c.get('symlink'): continue
        sym_path = os.path.join(env.base, 'Knowledge', c['symlink'])
        if os.path.exists(sym_path):
            desktop_name = f"Knowledge_{c['id']}.desktop"
            valid_kb_desktops.add(desktop_name)
            desktop_file = os.path.join(env.desktop, desktop_name)
            with open(desktop_file, 'w') as f:
                f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={c['name'].capitalize()}
Comment={i18n.T('generic_zim_comment')}
Exec=bash "{kiwix_script}" "{sym_path}"
Icon=accessories-dictionary
Terminal=false
""")
            os.chmod(desktop_file, 0o755)

    # Remove obsolete Knowledge icons (old versions or removed resources)
    for fname in os.listdir(env.desktop):
        if fname.startswith('Knowledge_') and fname.endswith('.desktop'):
            if fname not in valid_kb_desktops:
                stale = os.path.join(env.desktop, fname)
                os.remove(stale)
                log_info(i18n.T('obsolete_icon').format(fname))

    # 4. AI Models
    if not os.path.exists(env.ai_dir): return
    for m in AI_MODEL_CONFIG:
        pattern = m['filename'].replace('.', r'\.')
        matches = [f for f in os.listdir(env.ai_dir) if re.match(pattern, f)]
        if matches:
            best = sorted(matches)[-1]
            target = os.path.join(env.ai_dir, best)
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
            run_cmd(f"wget -c \"{appimage_url}\" -O \"{dest_path}\"")
        os.chmod(dest_path, 0o755)
        log_success(i18n.T('installed_appimage').format(name))
        return dest_path

    # PC - Level 2: Flatpak
    if flatpak_id:
        log_info(f"Jumping to Flatpak repository to resolve {name}...")
        run_cmd("sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo", quiet=True)
        if run_cmd(f"sudo flatpak install flathub {flatpak_id} -y", quiet=True):
            log_success(i18n.T('installed_flatpak').format(name))
            return True
            
    # PC - Level 3: APT
    if apt_deps:
        log_info(f"No portable options. Trying {name} via classic APT repository...")
        if run_cmd(f"sudo apt-get install -y {apt_deps}", quiet=True):
            log_success(i18n.T('installed_recursive_apt').format(name))
            return True
            
    log_err(i18n.T('install_failed').format(name))
    return False

# ==============================================================================
# SECTION 5: ADDITIONAL TOOLS (Basic Web Scraping)
# ==============================================================================

def fetch_url(url):
    """
    Performs a simple HTTP request and returns HTML/Text response.
    Simulates a traditional web browser User-Agent.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

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

    d.msgbox(diag_info, title=i18n.T('sys_diag_title'))

    # Depending on disk space, offer lightweight or enriched configurations
    lite_mode = sys_info.free_space_mb < 25000
    if lite_mode:
        log_info(i18n.T('lite_mode_msg'))
        def_kb = [0] # Only Wikipedia Top Miniatures
        def_ai = [0, 1]  # Suggest Minimum and Basic
    else:
        log_info(i18n.T('rich_mode_msg'))
        def_kb = [1] # Wikipedia full textual (11 GB)
        def_ai = [1, 2] # Suggest Basic and Intermediate

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

    # Detect ZIMs
    kb_opts = []
    for c in KNOWLEDGE_CONFIG:
        opt = {
            "label": c['label'],
            "name": c['name'],
            "type": c['type'],
            "id": c['id'],
            "search_url": c['search_url'],
            "symlink": c.get('symlink')
        }
        if os.path.exists(env.know_dir):
            prefix = "wikipedia" if c['name'] in ['wikipedia', 'wikimed'] else c['name']
            m_name = "_medicine" if c['name'] == 'wikimed' else ""
            pattern = rf"{prefix}_{sys_info.lang}{m_name}_{c['type']}_[0-9-]*\.zim"
            if any(re.match(pattern, f) for f in os.listdir(env.know_dir)):
                opt['installed'] = True
        kb_opts.append(opt)

    # Detect AI Models
    ai_opts = []
    for m in AI_MODEL_CONFIG:
        opt = {
            "label": m['label'],
            "filename": m['filename'],
            "url_base": m['url_base'],
            "symlink": m['symlink'],
            "id": m['id']
        }
        if os.path.exists(env.ai_dir):
            pattern = m['filename'].replace('.', r'\.')
            if any(re.match(pattern, f) for f in os.listdir(env.ai_dir)):
                opt['installed'] = True
        ai_opts.append(opt)

    # ==========================
    # INSTALLER QUESTIONNAIRES
    # ==========================

    kb_selected = multi_select_menu(d, i18n.T('kb_menu_title'), kb_opts, def_kb)

    install_maps = simple_question(d, i18n.T('maps_menu_title'), i18n.T('maps_menu_prompt'), default_yes=True)

    install_extras = simple_question(d, i18n.T('extras_menu_title'), i18n.T('extras_menu_prompt'), default_yes=True)

    ai_selected = multi_select_menu(d, i18n.T('ia_menu_title'), ai_opts, def_ai)

    use_torrent = simple_question(d, i18n.T('p2p_menu_title'), i18n.T('p2p_menu_prompt'), default_yes=False)
    
    if not simple_question(d, i18n.T('confirm_install_title'), i18n.T('confirm_install_prompt'), default_yes=True):
        log_err(i18n.T('install_aborted'))

    if os.environ.get("DEBUG") == "1":
        print(f"\n\033[1;33m[!] {i18n.T('warning')}:\033[0m {i18n.T('debug_simulation')}")
        sys.exit(0)

    # =========================================================
    # PHYSICAL EXECUTION AND INSTALLATION
    # =========================================================

    ensure_dirs(env)

    # Phase 1: OS Utilities Deployment
    log_info(i18n.T('fixing_perms'))
    run_cmd("sudo systemctl stop unattended-upgrades 2>/dev/null || true", quiet=True)
    run_cmd("sudo dpkg --configure -a", quiet=True)
    run_cmd("sudo apt-get install -f -y", quiet=True)
    run_cmd("sudo apt-get update", quiet=True)

    log_info(i18n.T('installing_base_deps'))
    
    base_pkgs = "python3 python3-dialog dialog aria2 pciutils wget curl bash jq rsync apt-utils flatpak cryptsetup epiphany-browser gedit xfce4-terminal dbus-user-session xdg-desktop-portal language-selector-common"
    if install_extras:
        log_info(i18n.T('adding_extras'))
        base_pkgs += " syncthing libreoffice vlc evince"
        
    run_cmd(f"sudo apt-get install -y {base_pkgs}", quiet=True)

    # System-wide language support synchronization
    log_info(i18n.T('syncing_lang_pkgs').format(sys_info.lang))
    run_cmd(f"check-language-support -l {sys_info.lang} 2>/dev/null | xargs sudo apt-get install -y", quiet=True)

    # System compatibility patches
    fix_flatpak_permissions()
    if sys_info.is_rpi:
        fix_rpi_pcmanfm_warnings()

    # Phase 2: Install Kiwix Visual Interface
    kiwix_appimage_url = None
    kiwix_appimage_name = None
    try:
        html = fetch_url("https://download.kiwix.org/release/kiwix-desktop/")
        matches = re.findall(r'href="(kiwix-desktop_x86_64_[0-9.-]*\.appimage)"', html)
        if matches:
            kiwix_appimage_name = sorted(matches)[-1]
            kiwix_appimage_url = f"https://download.kiwix.org/release/kiwix-desktop/{kiwix_appimage_name}"
    except Exception as e:
        print(f"\033[1;33m[!] {i18n.T('warning')}:\033[0m Error fetching Kiwix AppImage: {e}")

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

    # Phase 3: Knowledge Bases (ZIM)
    log_info(i18n.T('scanning_zim'))
    for idx in kb_selected:
        opt = kb_opts[idx]
        log_info(i18n.T('tracking_zim').format(opt['name'], opt['type']))
        zim_url = None
        zim_name = None
        
        try:
            html = fetch_url(opt['search_url'])
            prefix = "wikipedia" if opt['name'] in ['wikipedia', 'wikimed'] else opt['name']
            m_name = "_medicine" if opt['name'] == 'wikimed' else ""
            regex = rf'href="({prefix}_{sys_info.lang}{m_name}_{opt["type"]}_[0-9-]*\.zim)"'
            
            matches = re.findall(regex, html)
            if matches:
                 zim_name = sorted(matches)[-1]
                 zim_url = opt['search_url'] + zim_name
        except:
             pass
        
        if zim_name and zim_url:
             target_zim = os.path.join(env.know_dir, zim_name)
             if os.path.exists(target_zim) and not force_dl:
                  log_info(i18n.T('zim_exists').format(zim_name))
             else:
                  log_info(i18n.T('downloading_zim').format(zim_name))
                  if use_torrent:
                       run_cmd(f"aria2c --seed-time=0 --continue=true --dir=\"{env.know_dir}\" \"{zim_url}.torrent\"")
                  else:
                       run_cmd(f"aria2c -x 4 --continue=true --auto-file-renaming=false --dir=\"{env.know_dir}\" -o \"{zim_name}\" \"{zim_url}\"")
        else:
             log_err(i18n.T('zim_not_found').format(opt['name'], opt['type'], sys_info.lang))

    # Phase 4: Optional Cartographic Deployment (Organic Maps)
    repo_url = os.environ.get("REPO_URL", "https://raw.githubusercontent.com/Ganso/refugiOS/main")
    
    def fetch_script(s_name):
        d_path = os.path.join(env.scripts_dir, s_name)
        ok = run_cmd(f"wget -q \"{repo_url}/scripts/{s_name}\" -O \"{d_path}\"", quiet=True)
        if not ok or not os.path.exists(d_path) or os.path.getsize(d_path) == 0:
            local_dir = os.path.dirname(os.path.realpath(__file__))
            local_s = os.path.join(local_dir, "scripts", s_name)
            if os.path.exists(local_s):
                shutil.copy(local_s, d_path)
            else:
                log_err(i18n.T('script_not_found').format(s_name))
        os.chmod(d_path, 0o755)
        return d_path

    if install_maps:
        install_package(env, "Offline GPS Maps (Organic Maps)", sys_info.is_rpi, flatpak_id="app.organicmaps.desktop")
        
        if sys_info.is_rpi:
            run_cmd("sudo flatpak override --device=dri app.organicmaps.desktop", quiet=True)
        
        maps_script = fetch_script("refugios-maps.sh")
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
        os.chmod(maps_desktop, 0o755)
    else:
        log_info("Skipping Cartographic module (Organic Maps).")

    # Phase 5: AI Motor (Llamafile)
    if ai_selected:
        log_info("Establishing cognitive engine core foundations, Llamafile...")
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
                       run_cmd(f"wget -c \"{llama_url}\" -O \"{l_path}\"")
                  os.chmod(l_path, 0o755)
                  run_cmd(f"ln -sf '{l_path}' '{os.path.join(env.base, 'AI', 'llamafile')}'")
        except:
             log_err("Error connecting to GitHub for Llamafile.")

        for idx in ai_selected:
            opt = ai_opts[idx]
            full_url = opt['url_base'] + opt['filename']
            m_path = os.path.join(env.ai_dir, opt['filename'])
            if not os.path.exists(m_path) or force_dl:
                 log_info(f"Downloading file: {opt['filename']}...")
                 run_cmd(f"wget -c \"{full_url}\" -O \"{m_path}\"")
            run_cmd(f"ln -sf '{m_path}' '{os.path.join(env.base, 'AI', opt['symlink'])}'")

        script_path = fetch_script("refugios-ai-selector.sh")
        ai_assist_desktop = os.path.join(env.desktop, "AI_Assistant.desktop")
        with open(ai_assist_desktop, "w") as f:
             f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Local AI Assistant
Exec=xfce4-terminal -e "{script_path}"
Icon=utilities-terminal
Terminal=false
""")
        os.chmod(ai_assist_desktop, 0o755)

    # Phase 6: Privacy Cryptographic Foundations
    log_info("Assembling security vaults and privacy policies...")
    
    v_create = fetch_script("refugios-vault-create.sh")
    v_open = fetch_script("refugios-vault-open.sh")
    v_close = fetch_script("refugios-vault-close.sh")
    fetch_script("refugios-vault.py")

    # Ensure i18n.py is available in Scripts dir for vault manager
    i18n_src = os.path.join(os.path.dirname(os.path.realpath(__file__)), "i18n.py")
    i18n_dst = os.path.join(env.scripts_dir, "i18n.py")
    if os.path.exists(i18n_src):
        shutil.copy(i18n_src, i18n_dst)

    # Vault shortcuts names in the current language
    vault_names = {
        'en': ["1. Create new Secure Vault (First time only)", "2. Open Secure Vault", "3. Close and Seal Active Vault"],
        'es': ["1. Crear nueva Bóveda Segura (Sólo la primera vez)", "2. Abrir Bóveda Segura", "3. Cerrar y Sellar Bóveda Activa"]
    }
    current_vault_names = vault_names.get(sys_info.lang, vault_names['en'])

    for i, name, script, icon in [
        (1, current_vault_names[0], v_create, "dialog-password"),
        (2, current_vault_names[1], v_open, "folder-open"),
        (3, current_vault_names[2], v_close, "system-lock-screen")
    ]:
        dfile = os.path.join(env.desktop, f"{i}_{name.replace(' ', '_')}.desktop")
        with open(dfile, "w") as f:
            f.write(f"""[Desktop Entry]
Type=Application
Name={name}
Exec=xfce4-terminal -e "{script}"
Icon={icon}
Terminal=false
""")
        os.chmod(dfile, 0o755)

    # Desktop shortcut certification (Trusted marking)
    log_info("Certifying shortcuts and disabling desktop security warnings...")
    for file in os.listdir(env.desktop):
        if file.endswith('.desktop'):
            fpath = os.path.join(env.desktop, file)
            os.chmod(fpath, 0o755)
            # Mark as trusted (XFCE, GNOME, Wayland)
            if shutil.which("gio"):
                run_cmd(f"gio set '{fpath}' metadata::trusted yes", quiet=True)
                # SHA256 checksum for XFCE
                checksum = get_cmd_output(f"sha256sum '{fpath}' | awk '{{print $1}}'")
                if checksum:
                    run_cmd(f"gio set '{fpath}' metadata::xfce-exe-checksum '{checksum}'", quiet=True)
            run_cmd(f"attr -s trusted -V yes '{fpath}' 2>/dev/null || true", quiet=True)

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
    fetch_script("refugios-kiwix.sh")
    
    # Final resource synchronization
    if 'exec_path' not in locals():
         exec_path = "kiwix-desktop"
    sync_resources(env, sys_info, exec_path)

    log_success("GLOBAL DEPLOYMENT OPERATION FINISHED. Please check desktop icon integrity and accessibility.")


if __name__ == "__main__":
    main()
