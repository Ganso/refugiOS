#!/bin/bash
# ============================================
# refugiOS - Lanzador Bootstrapper
# (Prepara lo mínimo indispensable para Python)
# ============================================

set -e

# Funciones de color
log_info() { echo -e "\e[1;34m[*]\e[0m $1"; }
log_err()  { echo -e "\e[1;31m[X] ERROR:\e[0m $1"; exit 1; }

log_info "Comprobando dependencias iniciales del sistema..."

if [ "${DEBUG:-0}" == "1" ]; then
    echo -e "\e[1;33m[!] MODO DEBUG:\e[0m Análisis y dry-run. No se manipularán paquetes base."
else
    # Resolución de bloqueos de paquetes en Entornos Live
    sudo systemctl stop unattended-upgrades 2>/dev/null || true
    sudo dpkg --configure -a || true
fi

# Lista de dependencias del sistema necesarias para que el instalador de Python funcione bien
# pciutils provee 'lspci' usado para detectar la GPU/VRAM.
DEPENDENCIAS="python3 pciutils wget curl bash jq rsync apt-utils"

FALTAN=""
for pkg in $DEPENDENCIAS; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        FALTAN="$FALTAN $pkg"
    fi
done

if [ -n "$FALTAN" ]; then
    if [ "${DEBUG:-0}" == "1" ]; then
        echo -e "\e[1;33m[!] MODO DEBUG:\e[0m El sistema detectó faltantes ($FALTAN), pero no se descargarán."
    else
        log_info "Instalando dependencias mínimas requeridas:$FALTAN"
        sudo apt-get update -y >/dev/null 2>&1 || true
        sudo apt-get install -f -y < /dev/null || true
        sudo apt-get install -y $FALTAN < /dev/null
    fi
fi

# Lanzar instalador principal
export REPO_URL="https://raw.githubusercontent.com/Ganso/refugiOS/main"
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PYTHON_SCRIPT="/tmp/refugios_install.py"

log_info "Descargando instalador principal desde GitHub..."
if wget -q "$REPO_URL/install.py?nocache=$RANDOM" -O "$PYTHON_SCRIPT"; then
    log_info "Instalador descargado con éxito."
else
    echo -e "\e[1;33m[!] Aviso:\e[0m No se pudo descargar el instalador de internet."
    if [ -f "$SCRIPT_DIR/install.py" ]; then
        log_info "Usando install.py local como salvavidas fallback..."
        cp "$SCRIPT_DIR/install.py" "$PYTHON_SCRIPT"
    else
        log_err "Fallo crítico. Tampoco existe install.py local."
    fi
fi

log_info "Lanzando instalador Python..."
export HOME_DIR="$HOME"
export REPO_URL="$REPO_URL"
# Forzamos la lectura interactiva desde la terminal virtual (tty) 
# para solventar el 'EOFError' si el script maestro se lanzó a través de una tubería (pipe) como: curl ... | bash
python3 "$PYTHON_SCRIPT" < /dev/tty
