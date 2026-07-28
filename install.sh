#!/bin/bash
# ============================================
# refugiOS - Launcher Bootstrapper
# (Prepares the minimum indispensable for Python)
# ============================================

set -e

# Base directory setup
REFUGIOS_DIR="$HOME/refugiOS"
mkdir -p "$REFUGIOS_DIR/Scripts"

# Initial log functions (will be supplemented by i18n)
log_info() { echo -e "\e[1;34m[*]\e[0m $1"; }
log_err()  { echo -e "\e[1;31m[X] ERROR:\e[0m $1"; exit 1; }

# Important paths and URLs
REPO_URL="https://raw.githubusercontent.com/Ganso/refugiOS/main"
I18N_SH="$REFUGIOS_DIR/Scripts/i18n.sh"
PYTHON_SCRIPT="$REFUGIOS_DIR/install.py"
I18N_PY="$REFUGIOS_DIR/i18n.py"

# Define fallback localization function BEFORE sourcing
t() { echo "$1"; }
t_info="INFO"
t_error="ERROR"

# Developer Mode: when the installer is run from a checkout of the repository, the local
# files take precedence and nothing is fetched from GitHub. Otherwise local changes would
# be silently replaced by the published version and could never be tested.
LOCAL_SCRIPTS="$(dirname "$0")"
DEV_MODE=0
if [ -f "$LOCAL_SCRIPTS/install.py" ] && [ -f "$LOCAL_SCRIPTS/i18n.py" ]; then
    DEV_MODE=1
fi

if [ "$DEV_MODE" == "1" ]; then
    log_info "Developer Mode: using local files, skipping GitHub downloads."
    [ -f "$LOCAL_SCRIPTS/scripts/i18n.sh" ] && cp "$LOCAL_SCRIPTS/scripts/i18n.sh" "$I18N_SH"
    cp "$LOCAL_SCRIPTS/i18n.py" "$I18N_PY"
    cp "$LOCAL_SCRIPTS/install.py" "$PYTHON_SCRIPT"
else
    # Download localization system
    log_info "Fetching latest localization system..."
    wget -q "$REPO_URL/scripts/i18n.sh?nocache=$RANDOM" -O "$I18N_SH" || true
fi

# Try to source i18n if it exists and is not empty
if [ -s "$I18N_SH" ]; then
    source "$I18N_SH" || true
fi

log_info "$(t checking_deps)"

if [ "${DEBUG:-0}" == "1" ]; then
    echo -e "\e[1;33m[!] $(t warning):\e[0m $(t debug_mode)"
else
    # Resolve package locks in Live environments
    sudo systemctl stop unattended-upgrades 2>/dev/null || true
    sudo dpkg --configure -a || true
fi

# List of system dependencies needed for the Python installer to work well
DEPENDENCIES="python3 python3-dialog dialog aria2 pciutils wget curl bash jq rsync apt-utils flatpak"

MISSING=""
for pkg in $DEPENDENCIES; do
    if dpkg -s "$pkg" >/dev/null 2>&1; then
        echo -e "\e[1;34m[*]\e[0m $pkg: \e[1;32m[$(t installed)]\e[0m"
    else
        echo -e "\e[1;34m[*]\e[0m $pkg: \e[1;31m[$(t missing)]\e[0m"
        MISSING="$MISSING $pkg"
    fi
done

if [ -n "$MISSING" ]; then
    if [ "${DEBUG:-0}" == "1" ]; then
        echo -e "\e[1;33m[!] $(t warning):\e[0m The system detected missing packages ($MISSING), but they will not be downloaded."
    else
        log_info "$(t installing_deps) $MISSING"
        sudo apt-get update -y >/dev/null 2>&1 || true
        sudo apt-get install -f -y < /dev/null || true
        sudo apt-get install -y $MISSING < /dev/null
    fi
fi

# Download Python installer components
if [ "$DEV_MODE" != "1" ]; then
    log_info "$(t downloading_installer)"

    wget -q "$REPO_URL/i18n.py?nocache=$RANDOM" -O "$I18N_PY" || true

    if wget -q "$REPO_URL/install.py?nocache=$RANDOM" -O "$PYTHON_SCRIPT"; then
        log_info "$(t download_success)"
    else
        log_info "$(t download_fallback)"
    fi
fi

if [ ! -s "$PYTHON_SCRIPT" ]; then
    log_err "$(t fail_critical)"
fi

# The Python installer cannot start without its localization module
if [ ! -s "$I18N_PY" ]; then
    log_err "$(t fail_i18n)"
fi

log_info "$(t launching_python)"
export HOME_DIR="$HOME"
export REPO_URL="$REPO_URL"

# Force interactive reading from virtual terminal (tty)
# to solve 'EOFError' if the master script was launched through a pipe (like: curl ... | bash)
# No basta con comprobar que /dev/tty exista: sin terminal de control el fichero
# está ahí pero abrirlo falla, y la redirección tumbaría el instalador.
if (exec < /dev/tty) 2>/dev/null; then
    python3 "$PYTHON_SCRIPT" < /dev/tty
else
    echo -e "\e[1;33m[!] $(t warning):\e[0m $(t no_tty)"
    python3 "$PYTHON_SCRIPT"
fi
