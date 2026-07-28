# AGENTS.md — refugiOS

> Definitive guide for AI agents (and human contributors) working on the refugiOS
> codebase. Read this first before making any change.

---

## 1. Project Identity

**refugiOS** is a portable, **offline-first** Linux operating system designed as a
"digital refuge" for emergency and personal-resilience scenarios. It boots from a USB
on any PC or Raspberry Pi and carries offline Wikipedia, world maps, a private local AI
(LLM), LUKS-encrypted personal vaults, and survival guides — all working with zero
Internet dependency.

- **Paradigm:** "Prepare it today at home, use it when there's no Internet."
- **Distribution model:** A lightweight **base image (~16 GB)** is distributed; the user
  runs the installer **once while online** to download exactly the content they need
  (Wikipedia tier, AI model, maps, etc.). After that, the device operates 100% offline.
- **License:** GNU AGPL-3.0 (`LICENSE`).
- **Status:** First Beta, actively developed.
- **Current version:** `0.23` (see `CHANGELOG.md`). Versioning follows
  [Semantic Versioning](https://semver.org/spec/v2.0.0.html); the changelog follows
  [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- **Repository:** `https://github.com/Ganso/refugiOS.git` (branch `main`).
- **Primary language of maintainers:** Spanish — but **all code, comments, variable
  names, commit messages, and logic MUST be in English** (see `CONTRIBUTING.md`).
  User-facing strings and documentation are bilingual (ES + EN).

---

## 2. Repository Layout

```
refugiOS/
├── AGENTS.md                 # This file
├── CHANGELOG.md              # Version history (Keep a Changelog, written in Spanish)
├── CONTRIBUTING.md           # Bilingual EN/ES contributing guidelines
├── LICENSE                   # AGPL-3.0 full text
├── README.md                 # Primary README (Spanish)
├── README.en.md              # English README (mirror)
├── build_all.sh              # Convenience: builds ES + EN images, cleans logs
├── install.py                # MAIN installer — dialog-based TUI wizard (~1490 lines)
├── install.sh                # Bash bootstrapper (downloads + launches install.py)
├── i18n.py                   # Python localization system (EN/ES dictionary + T())
├── doc/                      # 26 bilingual .md docs (GitHub Wiki source)
├── media/                    # Branding + screenshots (see media/README.md)
│   ├── logo/                 # refugiOS.png, .ai, .pdf, fondo.png (wallpaper)
│   └── screenshots/          # Application screenshots, ES + EN
└── scripts/                  # Helper / runtime / build / test scripts
    ├── build_refugios.sh     # Image builder (debootstrap Debian Trixie + XFCE)
    ├── i18n.sh               # Bash localization system (parallel to i18n.py)
    ├── refugios-ai-selector.sh   # AI model selector + Llamafile launcher
    ├── refugios-kiwix.sh     # Kiwix/ZIM launcher (AppImage/Flatpak/binary)
    ├── refugios-maps.sh      # Organic Maps launcher (RPi software-rendering hack)
    ├── refugios-vault.py     # LUKS vault manager (create/open/close/delete, TUI)
    └── test_boot.sh          # QEMU UEFI boot test for generated images
└── tests/                    # Automated test suite (docs: doc/Test-Suite-EN.md)
    ├── README.md             # Pointer to the bilingual guides in doc/
    ├── run_all.sh            # Whole suite; --quick skips anything needing Docker
    ├── run_in_container.sh   # Runs a command in the privileged Debian container
    ├── docker/Dockerfile     # Test container (debootstrap, cryptsetup, shellcheck...)
    ├── lint.sh               # bash -n + py_compile (+ shellcheck when available)
    ├── unit_bash.sh          # i18n precedence, launchers, test_boot.sh arguments
    ├── unit_install.py       # install.py internals (downloads, dialog, exit code...)
    ├── test_install_sh.sh    # Bootstrapper: Developer Mode and validations
    ├── test_vault.sh         # Real LUKS vaults: password verification + full cycle
    ├── test_build.sh         # Real image build aborted on purpose inside the chroot
    ├── luks_pty.py           # Drives cryptsetup over a real terminal
    ├── qemu_boot_check.py    # Headless boot + screenshots at given moments
    ├── qemu_ctl.py           # Controls a running VM (keys, text, clicks, screenshots)
    └── prepare_e2e_image.sh  # Injects the local repo into an image for an E2E run
```

### Notable absences

There is **no** `package.json`, `requirements.txt`, `Makefile`, `pyproject.toml`,
`setup.py`, `.github/workflows/`, CI configuration, `.opencode/`, `opencode.json`, or
`CLAUDE.md`. Python dependencies are declared inline in `install.sh` /
`build_refugios.sh` and installed via apt at runtime.

There **is** an automated test suite under `tests/` (plain `unittest` + Bash, no test
framework to install), but **no CI**: nothing runs it automatically, so run
`bash tests/run_all.sh` yourself before proposing changes. Whatever needs root runs in a
privileged Docker container, so `sudo` is never required. Read `doc/Test-Suite-EN.md` first.

### Gitignored artifacts (never commit)

`.gitignore` protects: Python bytecode (`__pycache__/`), virtualenvs, OS metadata,
editor configs, and refugiOS-specific large binaries — `*.zim`, `*.gguf`, `*.img`,
`*.appimage`, `*.torrent`, `refugios_vars.fd`, `*.log`, `scripts/*.log`. A multi-GB
`refugios-base-*.img` and `refugios_vars.fd` may exist locally for testing; **never**
commit them.

---

## 3. Runtime Architecture

### Base OS & desktop
- **Pre-built image:** Debian Trixie + XFCE, natively installed (not a Live system).
- **Alternative:** Xubuntu LTS (24.04) or 25.10 Minimal, Live mode with persistence
  (BIOS/MBR-compatible path).
- **Desktop environment:** XFCE (low resource use; fresh boot < 1 GB RAM). On Raspberry
  Pi: Raspberry Pi OS with PCManFM/LightDM.
- **Display server:** Both X11 and Wayland supported; detected via `$XDG_SESSION_TYPE`.

### Target hardware
- **PC (x86_64):** Any Intel/AMD PC, boots from USB via UEFI (and BIOS/MBR via the
  Xubuntu method). Uses AppImages + Flatpaks + APT.
- **Raspberry Pi (ARM):** Certified on **RPi 3B+** (1 GB RAM) with Raspberry Pi OS
  64-bit. RPi 4/5 and Zero 2W theoretically functional but untested. The installer
  auto-detects ARM via `/proc/device-tree/model` and switches to native APT packages;
  Organic Maps is forced to software rendering on RPi 1/2/3/Zero (no OpenGL ES 3.0).

### Runtime directory layout (created by the installer at `~/refugiOS/`)
```
~/refugiOS/
├── Apps/versions/         # AppImage binaries (versioned, dated filenames)
├── Knowledge/versions/    # ZIM files (versioned, dated filenames)
├── AI/versions/           # GGUF model files + llamafile binary (versioned)
├── Vaults/                # LUKS vault container files (*.img)
└── Scripts/               # Deployed helper scripts + i18n.py + i18n.sh
```
`sync_resources()` in `install.py` symlinks the best (latest) versioned file in each
`versions/` dir to a stable name at the parent level (e.g. `Knowledge/wikipedia.zim`,
`AI/llamafile`, `AI/<tier>-model.gguf`). Desktop launchers reference the stable
symlinks.

Desktop directory is auto-detected as `~/Desktop` or `~/Escritorio` (Spanish locale).

---

## 4. Build & Image Generation

### `scripts/build_refugios.sh` (577 lines) — the image builder
Generates a base refugiOS disk image from scratch via `debootstrap`.

- **Must run as root.** Host must be Debian-based (debian|ubuntu|mint|pop), amd64.
- **Options:** `-s SIZE` (default `16G`; format `<num>[GMK]`), `-l LANG` (`es|en`,
  default `es`).
- **Output:** `refugios-base-<SIZE>-<LANG>.img` (sparse file).
- **Flow:** validate → install host deps (`debootstrap parted dosfstools e2fsprogs`) →
  `truncate` sparse image → GPT partition (BIOS_BOOT 1MiB, EFI FAT32 514MiB ESP, ROOT
  ext4) → `losetup -Pf` → format → mount → `debootstrap --arch=amd64 trixie` →
  generate `/etc/fstab` with real UUIDs → chroot: APT sources (main/contrib/non-free),
  install kernel + GRUB + XFCE + lightdm + firmware (iwlwifi, brcm, atheros, amd,
  nvidia) + flatpak, set locale/keyboard, install GRUB both UEFI-removable
  (`--removable --no-nvram`) and BIOS-MBR, create `refugios` user (passwordless sudo,
  LightDM autologin, screenlock disabled).
- **`trap cleanup EXIT`** robustly unmounts/detaches on any exit.
- **Full output tee'd** to `scripts/build_refugios_<timestamp>.log` (gitignored).
- **All injected user-facing strings are localized** at build time (es/en branches set
  ~30 variables).

### Scripts injected into the built image
| Injected path | Purpose |
|---|---|
| `/usr/local/bin/refugios-expand.sh` + `.service` | First-boot auto-grow of root partition via `growpart`+`resize2fs`; self-disabling after one run. |
| `/usr/local/bin/refugios-install-wrapper.sh` | Connectivity check (`ping github.com`) + launches installer; zenity/console fallback if offline. Also recreated by `install.py` (`ensure_install_icon`). |
| `/usr/local/bin/refugios-trust-launcher.sh` + autostart | Marks `.desktop` files as XFCE-trusted via `gio set metadata::xfce-exe-checksum` (SHA-256). |
| `/usr/local/bin/refugios-welcome.sh` + autostart | First-boot zenity welcome popup showing disk size; guarded by `~/.refugios-welcome-done` marker. |
| `Instalar_refugiOS.desktop` (skel + user Desktop) | "Complete refugiOS installation" launcher that re-runs the installer. |

### `build_all.sh` (top-level)
Convenience wrapper: `sudo ./scripts/build_refugios.sh -l es && sudo ./scripts/build_refugios.sh -l en && sudo rm -f ./scripts/*.log`.

### `scripts/test_boot.sh` (135 lines) — the test script
Boots a generated image in QEMU with UEFI (OVMF) to verify GRUB → LightDM autologin →
XFCE desktop with installer launcher and welcome popup.

- **Does NOT require root** (unless KVM perms needed).
- Supports more host distros than `build_refugios.sh` (Debian/Ubuntu/Mint/Pop/Fedora/
  Arch/Manjaro/openSUSE).
- Auto-finds `refugios-base-*.img` in workspace, or accepts a size arg.
- Detects OVMF firmware across distro-specific paths; creates writable
  `refugios_vars.fd` copy; detects KVM (`/dev/kvm`); 8 GB RAM, 2 CPUs, virtio VGA, NAT.
- **Run:** `bash scripts/test_boot.sh [-s SIZE] [-l LANG]` (the old positional
  `test_boot.sh SIZE` still works; images are named `refugios-base-SIZE-LANG.img`).
- RAM is derived from the host's available memory, clamped to [2G, 8G].

---

## 5. The Installer — `install.py`

The core of the project. A `dialog`-based TUI wizard (~1490 lines). Must run as a
**normal user** (NOT root); uses `sudo` internally.

### Imports
`os, sys, subprocess, urllib.request, json, shutil, re, time, random` (stdlib) +
`i18n` (local) + `dialog` (`python3-dialog`, required).

### Configuration dicts (top of file — edit these to change content offerings)
- **`WIKIPEDIA_CONFIG`** — 3 ZIM tiers: `wiki_lite` (~73 MB top articles, no images),
  `wiki_nopics` (~11.5 GB full text), `wiki_total` (~38 GB with images). Fields: `id`,
  `name`, `label`, `type`, `search_url`, `priority`, `size_mb`.
- **`OTHER_WIKIS_CONFIG`** — `wikimed` (~620 MB) and `wikihow` (~20 GB, multiple
  mirrors). Fields include `symlink`, `search_urls` (list).
- **`AI_MODEL_CONFIG`** — 5 LLM GGUF models, all from `huggingface.co/unsloth`:
  | id | model | size | symlink |
  |---|---|---|---|
  | `ia_min` | Qwen3-0.6B-Q4_K_M | ~380 MB | minimal-model.gguf |
  | `ia_base` | gemma-4-E4B-it-Q4_K_M | ~4.7 GB | basic-model.gguf |
  | `ia_med` | Qwen3-8B-Q4_K_M | ~4.8 GB | intermediate-model.gguf |
  | `ia_max` | Qwen3-14B-Q4_K_M | ~8.6 GB | advanced-model.gguf |
  | `ia_ultra` | gemma-4-26B-A4B-it-UD-Q4_K_M | ~16.2 GB | ultra-model.gguf |

  > **Keep in sync** with the `register_model` calls in
  > `scripts/refugios-ai-selector.sh` when modifying AI models.

### Key classes & functions
- `FAILED_ITEMS = []` — global accumulator for non-fatal failures (shown in final
  summary).
- `_write_log(msg)` — strips ANSI codes (regex) and appends to
  `/tmp/refugios-install.log`.
- `log_info(msg)` / `log_success(msg)` — colored console + log file.
- `log_err(msg, fatal=True)` — red error; `fatal=True` → `sys.exit(1)`;
  `fatal=False` → append to `FAILED_ITEMS` and continue.
- `SizeLogger` — tracks disk space per phase (`log_section`, `log_total`).
- `run_cmd(cmd, shell=True, check=True, quiet=False)` — subprocess wrapper returning
  bool.
- `download_with_aria2(url, dest_path, timeout=120, max_tries=3)` — aria2c with 8
  parallel connections, strict Linux `timeout` wrapper, cleans `.aria2` control +
  partial files (success or failure).
- `get_cmd_output(cmd)` — captures stdout.
- `certify_icon(fpath)` / `certify_all_desktop_icons(desktop_dir)` — marks `.desktop`
  files as XFCE-trusted via `gio set metadata::xfce-exe-checksum` (SHA-256).
- `OBSOLETE_EXEC_PATTERNS` + `cleanup_obsolete_icons(desktop_dir)` — removes old vault
  script icons from previous refugiOS versions.
- `ensure_install_icon(env, sys_info)` — creates
  `/usr/local/bin/refugios-install-wrapper.sh` + desktop re-install icon if missing.
- `set_wallpaper(sys_info)` — sets `media/logo/fondo.png` for XFCE (`xfconf-query`) and RPi
  (`pcmanfm`).
- `SystemInfo` — detects OS (Ubuntu/Debian/RPi via `/etc/os-release` +
  `/proc/device-tree/model`), RAM (`/proc/meminfo`), storage (`shutil.disk_usage`),
  GPU/VRAM (`lspci`), desktop env, language.
- `fix_flatpak_permissions()` — AppArmor unprivileged-userns patch for Ubuntu 24.04 /
  Debian 13.
- `fix_rpi_pcmanfm_warnings()` — disables PCManFM non-exec warning on RPi.
- `sanitize_for_dialog(text)` — **CRITICAL**: replaces Unicode typographic chars
  (`•` U+2022, `–`, `—`, smart quotes, `…`) with ASCII equivalents and encodes to
  latin-1 with `replace`. The `dialog` library encodes strings as **latin-1**, so any
  non-ASCII user-facing string passed to `d.msgbox`/`d.menu`/etc. MUST be wrapped in
  this function or it will raise `UnicodeEncodeError`.
- `init_dialog()`, `multi_select_menu`, `single_select_menu`, `simple_question` — TUI
  primitives wrapping `dialog`. Installed items are tagged with `\Z1...installed_tag...\Zn`
  (red) and pre-checked.
- `TargetEnv` — central path map under `~/refugiOS/`.
- `sync_resources(env, sys_info, exec_path)` — symlinks best ZIM/AI versions to stable
  names; creates/removes desktop launchers; cleans stale Knowledge icons.
- `ensure_dirs(env)` — creates the `~/refugiOS/` structure.
- `install_package(env, name, is_rpi, appimage_url, appimage_name, flatpak_id, apt_deps)`
  — **the cascading installer engine** (see §7).
- `fetch_url(url)` — simple HTTP GET with browser User-Agent.
- `main()` — orchestrates the full flow (see below).

### `main()` flow
1. Root-guard (`os.geteuid() == 0` → exit).
2. Init dialog.
3. Detect `SystemInfo`.
4. Language selection (persistent via `i18n.save_lang`).
5. System diagnosis dialog.
6. Storage-mode presets: lite (<30 GB), standard (30–70 GB), rich (>70 GB) → default
   Wikipedia tier, other wikis, AI models.
7. Rewrite-mode question (force re-download).
8. Detect already-installed components (scan `versions/` dirs).
9. Questionnaires: Wikipedia (single), other wikis (multi), maps (yes/no), extras
   (yes/no), AI models (multi), P2P preference (yes/no).
10. Space estimation + critical-space warning + confirmation.
11. `DEBUG=1` → dry-run exit (no changes, no downloads).
12. **Execution phases:**
    - **Phase 1:** OS utilities & base deps (apt packages, language packs, AppArmor
      patch, RPi PCManFM patch).
    - **Phase 2:** Kiwix Desktop (AppImage via scraped download.kiwix.org → Flatpak →
      APT).
    - **Phase 3:** Knowledge bases / ZIMs (Wikipedia tier + other wikis; mirror
      cascade → BitTorrent fallback).
    - **Phase 4:** Organic Maps (Flatpak) + `refugios-maps.sh` launcher.
    - **Phase 5:** AI engine (Llamafile from GitHub releases) + selected GGUF models +
      `refugios-ai-selector.sh` launcher.
    - **Phase 6:** Vault (`refugios-vault.py` + `i18n.py` deployed) + desktop icon.
    - Wrapper install icon, PCManFM quick-exec hack, `refugios-kiwix.sh` fetch,
      `sync_resources`, `set_wallpaper`, certify all icons, `SizeLogger` total.
13. **Final report:** if `FAILED_ITEMS` → error summary dialog (dashes, not bullets);
    else → success dialog with total space used.

---

## 6. Other Key Scripts

### `install.sh` (107 lines) — bootstrap
Prepares the minimum for the Python installer. `set -e`; creates `~/refugiOS/Scripts`;
defines fallback `t()`; **Developer Mode** copies local `scripts/i18n.sh`, `i18n.py`,
`install.py` if present; otherwise downloads them from GitHub raw; sources `i18n.sh`;
checks/installs deps (`python3 python3-dialog dialog aria2 pciutils wget curl bash jq
rsync apt-utils flatpak`); runs `python3 install.py < /dev/tty` (forces interactive
tty to fix `EOFError` from `curl|bash` pipes). `DEBUG=1` skips apt operations.

### `scripts/refugios-vault.py` (564 lines) — LUKS vault manager
Interactive `dialog` TUI for create/open/close/delete encrypted LUKS containers.

- **Imports:** `os, sys, subprocess, shutil, re, json, math` + `i18n` + `dialog`. Has a
  `/dev/tty` stdin fix for piped launches.
- **Vaults stored as** `~/refugiOS/Vaults/<name>.img`; mapper name `vault_<name>`;
  mount point `~/Desktop/VAULT_<name>` (or `~/Escritorio/...`).
- **Operations:** `op_create` (`dd` → `cryptsetup luksFormat` → `mkfs.ext4`),
  `op_open`, `op_close` (`umount` + `cryptsetup close`), `op_delete`.
- **USB import:** `detect_usb_drives` via `lsblk -J`; suggests 1.5× used data;
  `_import_usb_to_vault` rsyncs USB → vault.
- **Root-guard**; uses `sudo cryptsetup` for all LUKS ops.
- **`os.system('clear')`** runs after each `yesno` confirmation before launching
  commands, for clean terminal output.

### `scripts/refugios-ai-selector.sh` (191 lines)
Detects RAM (`free -m`) + VRAM (NVIDIA `nvidia-smi`, AMD `/sys/class/drm/.../mem_info_vram_total`,
Intel iGPU shares RAM); computes `USABLE_MB = RAM + VRAM - 2048` (strict 2 GB OS safety
margin to avoid USB swap freeze); registers 5 models with `min_usable_mb` thresholds;
builds `dialog` menu showing only installed models with `[OK]`/`[LOW_RAM]` status and
auto-preselecting the most powerful fitting model; on launch sets `-ngl 99` (full GPU
offload) if dedicated GPU, `-ngl 0` if no AVX2 (avoids crashes on old/ARM CPUs); starts
`llamafile --server` on port 8080; opens `epiphany-browser` (or `xdg-open`) to the chat
UI. Runs `clear` after the dialog before launching llamafile.

### `scripts/refugios-kiwix.sh` (55 lines)
Launches a ZIM file with Kiwix Desktop. Resolves symlinks via `readlink -f` (Flatpak
sandbox can't follow them); detects Kiwix binary in order: `kiwix-desktop` in PATH →
`~/refugiOS/Apps/kiwix-desktop.appimage` (with `APPIMAGE_EXTRACT_AND_RUN=1`) → Flatpak
`org.kiwix.desktop` (with `--filesystem="${ZIM_DIR}:ro"` for sandbox access) → any
kiwix AppImage found in `Apps/`.

### `scripts/refugios-maps.sh` (19 lines)
Launches Organic Maps (Flatpak). Detects RPi 1/2/3/Zero via
`/proc/device-tree/model`; forces `LIBGL_ALWAYS_SOFTWARE=1` on those; otherwise normal
`flatpak run app.organicmaps.desktop`.

---

## 7. Installer Cascade (AppImage → Flatpak → APT)

`install_package()` in `install.py`:

- **Raspberry Pi path:** Overrides priorities → tries native APT first (many AppImages
  lack ARM builds); skips if no APT package.
- **PC path (3 levels):**
  1. **AppImage** via direct download with `aria2c` → `chmod +x`. (Returns the path
     string on success.)
  2. **Flatpak** — adds flathub remote if missing, `flatpak install flathub <id> -y`.
  3. **APT** — `sudo apt-get install -y <deps>`.
  - If all 3 fail → `log_err(..., fatal=False)` appends to `FAILED_ITEMS` and
    continues. **The installer never hard-stops on a single package failure.**

**ZIM download cascade** (separate): multiple `search_urls` in order → English fallback
if requested language missing → BitTorrent (`.torrent`) fallback → logged as failed
(`fatal=False`).

---

## 8. i18n / Localization System

**Dual implementation** mirroring each other. Supported languages: **`es` (Spanish)
and `en` (English) only** — hardcoded in validation lists. Roadmap mentions expanding.

### `i18n.py` (Python) — used by `install.py` and `refugios-vault.py`
- Global `REFUGIOS_LANG = "en"`; config file `~/.refugios_lang`.
- `load_lang()` (called at import): reads config file → else autodetects from `$LANG`
  env (splits on `_`, lowercases, checks es/en).
- `save_lang(lang)`: writes config file + patches `~/.bashrc` with
  `export LANG=<lang>_<ES|US>.UTF-8` for session persistence.
- `TRANSLATIONS` dict: two sub-dicts `'en'` and `'es'`, ~150 keys each.
- `T(key)`: 3-level fallback — `TRANSLATIONS[REFUGIOS_LANG].get(key)` →
  `TRANSLATIONS['en'].get(key)` → `key` itself.
- **Key naming:** snake_case (e.g. `sys_diag_title`, `vault_create_title`,
  `install_finished_msg`). Placeholders use positional `{0}`, `{1}` via `.format()`.
- **Known gap:** `setting_wallpaper` is referenced in `install.py` but not defined in
  `i18n.py` — handled via `try/except` fallback to a Spanish literal.

### `scripts/i18n.sh` (Bash) — used by `install.sh`, `refugios-kiwix.sh`,
`refugios-maps.sh`, `refugios-ai-selector.sh`
- Same `~/.refugios_lang` config + `$LANG` autodetect.
- Variables named `t_<lang>_<key>`; `t()` function echoes `${!varname}` with English
  fallback. `export REFUGIOS_LANG` propagates to child processes.

### `scripts/build_refugios.sh`
Has its own inline es/en string blocks (welcome text, wrapper messages, auto-expand
messages) resolved at image build time.

### Convention when adding a user-facing string
Add the key to **BOTH** `i18n.py` (en + es dicts) **AND** `i18n.sh` (if used by a bash
script), plus any build-script inline block if relevant. Keep keys grouped logically
with inline comments.

---

## 9. Dialog TUI Conventions

- Uses `python3-dialog` (the `dialog` library wrapping ncurses `dialog`).
- `init_dialog()` enables `--colors` for `\Z1` (red) tags marking installed items.
- Three primitives: `multi_select_menu` (`d.checklist`), `single_select_menu`
  (`d.menu`), `simple_question` (`d.yesno`).
- **CRITICAL latin-1 constraint:** `dialog` encodes strings as **latin-1**. Any
  non-ASCII user-facing string passed to `d.msgbox`/`d.menu`/`d.checklist`/`d.yesno`
  MUST be wrapped in `sanitize_for_dialog()` or it will raise `UnicodeEncodeError`.
  Error summaries use `-` instead of `•` to avoid this.
- **Screen clear:** `os.system('clear')` (Python) / `clear` (Bash) is run after each
  dialog→command transition for clean terminal output. This is applied in
  `install.py` (after the "INSTALLATION STARTING" dialog and after each missing-script
  warning), `scripts/refugios-vault.py` (after each `yesno` confirmation, before
  launching `dd`/`cryptsetup`/`mount`/`umount`/`rsync`/`os.remove`), and
  `scripts/refugios-ai-selector.sh` (after the model menu, before launching llamafile).

---

## 10. Logging & Error-Handling Conventions

### Logging
- **Console:** ANSI-colored prefixes — `[*]` blue (info), `[X] ERROR:` red,
  `[v] SUCCESS:` green, `[!] WARNING:` yellow.
- **File:** `/tmp/refugios-install.log` — ANSI codes stripped via regex; every `log_*`
  writes there.
- **Build log:** `scripts/build_refugios_<timestamp>.log` (tee'd, gitignored).
- `SizeLogger` records disk usage per phase with `[Size Log] [Phase Name]` markers.

### Error handling
- `log_err(msg, fatal=True)` exits; `log_err(msg, fatal=False)` appends to global
  `FAILED_ITEMS` and continues. **The installer favors graceful degradation** — a
  single component failure never hard-stops the whole install.
- **Critical-script pre-validation:** `refugios-vault.py`, `refugios-kiwix.sh`, and
  `refugios-ai-selector.sh` are checked with `os.path.isfile()` after `fetch_script()`.
  If missing: warn the user (log + `d.msgbox` with a descriptive i18n message), skip
  their desktop icon, and **continue** the installation. Dedicated i18n keys:
  `vault_script_missing`, `kiwix_script_missing`, `ai_script_missing`.
- **Root-guard:** `install.py` and `refugios-vault.py` refuse to run as root
  (`os.geteuid() == 0` → exit) and use `sudo` only internally.
- **Downloads** are wrapped with Linux `timeout` to prevent indefinite hangs; `.aria2`
  control + partial files are always cleaned (success or failure).

---

## 11. Documentation (`doc/`)

26 bilingual `.md` files (ES + EN mirrored pairs), GitHub Wiki format. Also
`Home.md` (wiki landing) and `_Sidebar.md` (wiki nav).

| Topic | ES file | EN file |
|---|---|---|
| Vision & user experience | `Vision-y-Experiencia-ES.md` | `Vision-and-User-Experience-EN.md` |
| System architecture | `Arquitectura-ES.md` | `System-Architecture-EN.md` |
| Comparison of solutions | `Soluciones-Existentes-ES.md` | `Comparison-of-Solutions-EN.md` |
| Choosing install media | `Eleccion-Medio-Instalacion-ES.md` | `Choosing-Installation-Media-EN.md` |
| Virtualization guide | `Guia-Virtualizacion-y-Pendrive-ES.md` | `Virtualization-Guide-EN.md` |
| Xubuntu installation | `Instalacion-Xubuntu-ES.md` | `Xubuntu-Installation-EN.md` |
| Raspberry Pi installation | `Instalacion-Raspberry-ES.md` | `Raspberry-Pi-Installation-EN.md` |
| System image build | `Construccion-Imagen-Sistema-ES.md` | `System-Image-Build-EN.md` |
| Compatibility table | `Compatibilidad-ES.md` | `Compatibility-EN.md` |
| Security vaults | `Bovedas-Criptograficas-ES.md` | `Security-Vaults-EN.md` |
| Unit cloning | `Clonado-de-Pendrive-ES.md` | `Cloning-Units-EN.md` |
| Modules & roadmap | `Modulos-y-Roadmap-ES.md` | `Modules-and-Roadmap-EN.md` |

**When updating docs, update both the ES and EN pair.** Roadmap items (Khan Academy,
Kolibri, Project Gutenberg, SDR, games, auto-updater, more i18n) live in
`Modulos-y-Roadmap-ES.md` / `Modules-and-Roadmap-EN.md`.

---

## 12. Development Workflow & Conventions

### Branch & commit
- Fork → branch `feature/<name>`.
- **Commit messages in English**, conventional-commits-like prefixes (`fix:`, `feat:`,
  `docs:`, `chore:`).
- Link PRs to Issues; discuss feature requests via Issues first.
- **All code comments, variable names, and logic in English** (per `CONTRIBUTING.md`).
- **DO NOT add comments to code unless asked.** Match existing style.

### Coding style
- **Python:** PEP-8-ish, 4-space indent, module docstrings, type-free. Section banners
  with `# =====...` comment blocks. Short function docstrings.
- **Bash:** `set -e` in critical scripts, `trap cleanup EXIT` for robust teardown,
  localized string variables.

### Verification before finishing a task
There is no `npm run lint` / `ruff` / `typecheck`. After editing Python, verify syntax:
```bash
python3 -m py_compile install.py
python3 -m py_compile i18n.py
python3 -m py_compile scripts/refugios-vault.py
```
After editing Bash:
```bash
bash -n install.sh
bash -n scripts/refugios-ai-selector.sh
bash -n scripts/refugios-kiwix.sh
bash -n scripts/refugios-maps.sh
bash -n scripts/build_refugios.sh
bash -n scripts/test_boot.sh
```

### Automated tests
```bash
bash tests/run_all.sh          # whole suite (needs Docker; ~3-4 min)
bash tests/run_all.sh --quick  # only what runs on the host
```
See `doc/Test-Suite-EN.md` for running individual tests, building images without `sudo`,
and driving a full installation inside QEMU.

### Dry-run / debug
- `DEBUG=1 python3 install.py` (or `DEBUG=1 ... install.sh`) — dry-run simulation: no
  system changes, no downloads, exits before execution phases.
- `bash scripts/test_boot.sh` — boot-test a built image in QEMU UEFI.

### Releases
The project follows **Keep a Changelog** + **Semantic Versioning**. On a release:
1. Add a new `## [X.Y] - YYYY-MM-DD` entry to `CHANGELOG.md` (Spanish, with
   Corregido / Añadido / Cambiado / Eliminado subsections).
2. Bump the version badge in **both** `README.md`
   (`Versi%C3%B3n-X.Y`) and `README.en.md` (`Version-X.Y`).
3. Update the "Historial de Versiones" / "Version History" section in both READMEs.

---

## 13. Common Pitfalls

1. **`UnicodeEncodeError` with `dialog` (latin-1).** Any non-ASCII char (bullets `•`,
   em-dashes, smart quotes, accented letters beyond latin-1) passed to a `dialog` call
   will crash. Always wrap user-facing text in `sanitize_for_dialog()`. Use `-` instead
   of `•` in summaries.
2. **Forgetting `i18n` keys in both languages.** Add new keys to `en` AND `es` dicts in
   `i18n.py`, and to `i18n.sh` if a bash script uses them. `T()` falls back to English
   then to the key itself, so a missing key shows the raw key name to the user.
3. **Desync between `AI_MODEL_CONFIG` (install.py) and `register_model` calls
   (refugios-ai-selector.sh).** Keep them in sync when adding/removing/renaming models.
4. **Committing large binaries.** `*.img`, `*.zim`, `*.gguf`, `*.appimage` are
   gitignored — never `git add` them.
5. **Running the installer as root.** `install.py` and `refugios-vault.py` hard-refuse
   root; they use `sudo` only internally for specific commands.
6. **`curl|bash` stdin issue.** `install.sh` runs `python3 install.py < /dev/tty` to
   fix `EOFError` when launched via a piped curl. Preserve this when modifying
   `install.sh`.
7. **Flatpak sandbox can't follow symlinks.** `refugios-kiwix.sh` resolves symlinks
   with `readlink -f` and adds `--filesystem` for Flatpak. Keep this when touching ZIM
   launching.
8. **XFCE `.desktop` trust.** `.desktop` files must be certified via
   `gio set metadata::xfce-exe-checksum` (`certify_icon`) or XFCE will show a
   "untrusted application" prompt. `certify_all_desktop_icons` runs at the end of
   install; `refugios-trust-launcher.sh` does it on first boot of a built image.

---

## 14. Quick Reference — File Cheat Sheet

| File | Role | Lines |
|---|---|---|
| `install.py` | Main TUI installer wizard | ~1490 |
| `i18n.py` | Python localization (EN/ES) | ~384 |
| `install.sh` | Bootstrap launcher | ~107 |
| `scripts/refugios-vault.py` | LUKS vault manager TUI | ~564 |
| `scripts/refugios-ai-selector.sh` | AI model selector + llamafile launcher | ~191 |
| `scripts/refugios-kiwix.sh` | Kiwix/ZIM launcher | ~55 |
| `scripts/refugios-maps.sh` | Organic Maps launcher | ~19 |
| `scripts/build_refugios.sh` | Image builder (debootstrap) | ~577 |
| `scripts/test_boot.sh` | QEMU UEFI boot test | ~135 |
| `scripts/i18n.sh` | Bash localization | ~120 |
| `build_all.sh` | Build both ES+EN images | 2 |
| `tests/run_all.sh` | Entry point for the whole test suite | ~44 |
| `tests/unit_install.py` | Unit tests for `install.py` | ~290 |
| `tests/unit_bash.sh` | Tests for the Bash scripts | ~219 |
| `doc/Test-Suite-EN.md` | How the tests work and how to run them | ~250 |

---

## 15. When You're Asked to Make Changes

1. **Understand the request** — re-read the relevant file(s) with `Read`/`Grep`/`Glob`
   before editing.
2. **Follow existing conventions** — mimic code style, use existing libraries
   (`i18n.T`, `run_cmd`, `log_*`, `sanitize_for_dialog`), don't introduce new deps.
3. **No comments unless asked.**
4. **i18n every user-facing string** — add keys to both `en` and `es` in `i18n.py`
   (and `i18n.sh` if bash).
5. **Wrap dialog text in `sanitize_for_dialog()`** if it could contain non-ASCII.
6. **Verify syntax** with `python3 -m py_compile` / `bash -n` after editing, and run
   `bash tests/run_all.sh` before proposing the change.
7. **Add a test** for any behaviour you fix, and check it fails without your fix.
8. **Update `CHANGELOG.md`** and **both READMEs** (version badge + history section)
   when releasing a new version.
8. **Never commit unless explicitly asked.** Stage only intended files; never commit
   secrets or gitignored binaries.
