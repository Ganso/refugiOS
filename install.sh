#!/bin/bash
# ============================================
# refugiOS - Instalador del Sistema
# (Preparación del entorno y aplicaciones)
# ============================================

# Detener la ejecución si hay errores críticos o variables sin definir
set -euo pipefail

# Funciones de color para un log limpio y legible
log_info() { echo -e "\e[1;34m[*]\e[0m $1"; }
log_err()  { echo -e "\e[1;31m[X] ERROR:\e[0m $1"; exit 1; }
log_success() { echo -e "\e[1;32m[v] ÉXITO:\e[0m $1"; }

# ============================================
# Detección de Recursos
# ============================================
TOTAL_MB=$(df -m / | awk 'NR==2 {print $2}')
FREE_MB=$(df -m / | awk 'NR==2 {print $4}')
SYS_LANG=$(echo "${LANG:-es}" | cut -d'_' -f1)
IS_RPI=0
[ -f /sys/firmware/devicetree/base/model ] && grep -q "Raspberry Pi" /sys/firmware/devicetree/base/model && IS_RPI=1

if [ "$IS_RPI" -eq 1 ]; then
    echo -e "\n\e[1;33m[!] ADVERTENCIA DE COMPATIBILIDAD:\e[0m"
    echo "Se ha detectado que estás corriendo en una Raspberry Pi."
    echo "El soporte para esta plataforma es todavía PRELIMINAR."
    echo "Existen fallos conocidos (Kiwix ARM, OpenGL de Mapas, IA) y se esperan errores."
    echo ""
    read -p "¿Deseas continuar con la instalación bajo tu responsabilidad? (s/N): " rpi_confirm < /dev/tty
    if [ "${rpi_confirm,,}" != "s" ]; then
        log_err "Instalación cancelada por el usuario (Raspberry Pi Beta)."
    fi
fi

log_info "Espacio asignado en raíz: ${TOTAL_MB} MB. Libre: ${FREE_MB} MB."

# Autoselección según capacidad (menor a 25GB -> modo Lite)
if [ "$TOTAL_MB" -lt 25000 ]; then
    DEF_WIKI="2"  # Top Mini
    DEF_HOWTO="n" # Omitir Wikihow
    DEF_IA="3"    # Omitir IA
    log_info "Capacidad reducida detectada. Se recomendarán versiones ligeras."
else
    DEF_WIKI="1"  # All NoPic
    DEF_HOWTO="n" # Omitir Wikihow por defecto (pesado)
    DEF_IA="1"    # Incluir IA (básico)
    log_info "Capacidad óptima detectada. Se recomendarán versiones completas."
fi

# ============================================
# Menú Interactivo de Instalación
# ============================================
echo ""
echo -e "\e[1;36m=== CONFIGURACIÓN DE REFUGIOS ===\e[0m"

# 1. Forzar descargas
read -p "¿Quieres volver a descargar los archivos que ya existen? (s/N): " menu_force < /dev/tty
if [ "${menu_force,,}" == "s" ]; then FORCE=1; else FORCE=0; fi

# 2. Idioma
echo ""
echo "Selecciona el idioma principal para los datos offline (sistema: $SYS_LANG):"
echo "  1) Español (es)"
echo "  2) Inglés (en)"
echo "  3) Francés (fr)"
read -p "Opción [1-3] (Enter para autodetectado): " menu_lang < /dev/tty
case "$menu_lang" in
    1) WIKI_LANG="es" ;;
    2) WIKI_LANG="en" ;;
    3) WIKI_LANG="fr" ;;
    *) WIKI_LANG="$SYS_LANG" ;;
esac
if [[ ! "$WIKI_LANG" =~ ^(es|en|fr)$ ]]; then WIKI_LANG="es"; fi

# 3. Wikipedia
echo ""
echo "¿Qué versión de la Wikipedia deseas descargar?"
echo "  1) Completa sin imágenes (~11 GB)"
echo "  2) Top Mini (~200 MB)"
echo "  3) Ninguna (Omitir)"
read -p "Opción [1-3] (Enter para la recomendada: $DEF_WIKI): " menu_wiki < /dev/tty
menu_wiki=${menu_wiki:-$DEF_WIKI}
if [ "$menu_wiki" == "1" ]; then
    WIKI_TYPE="all_nopic"
    DOWNLOAD_WIKI=1
elif [ "$menu_wiki" == "2" ]; then
    WIKI_TYPE="top_mini"
    DOWNLOAD_WIKI=1
else
    DOWNLOAD_WIKI=0
fi

# 4. WikiMed (Medicina)
echo ""
echo "¿Deseas descargar WikiMed (Enciclopedia Médica)? (~1.5 GB)"
read -p "Opción (S/n) [Enter para S]: " menu_med < /dev/tty
if [ "${menu_med,,}" == "n" ]; then DOWNLOAD_MED=0; else DOWNLOAD_MED=1; fi

# 5. WikiHow (Manuales)
echo ""
echo "¿Deseas descargar WikiHow (Manuales de supervivencia)? (~25-50 GB según idioma)"
read -p "Opción (s/N) [Enter para la recomendada: $DEF_HOWTO]: " menu_howto < /dev/tty
menu_howto=${menu_howto:-$DEF_HOWTO}
if [ "${menu_howto,,}" == "s" ]; then DOWNLOAD_HOWTO=1; else DOWNLOAD_HOWTO=0; fi

# 5. Inteligencia Artificial
echo ""
echo "¿Qué nivel de asistente de IA deseas instalar?"
echo "  1) Solo modelo básico - Phi-4-mini (~2.5 GB, funciona en cualquier PC)"
echo "  2) Pack completo - Tres niveles según potencia (~16.5 GB total)"
echo "  3) No, omitir IA"
read -p "Opción [1-3] (Enter para la recomendada: $DEF_IA): " menu_ia < /dev/tty
menu_ia=${menu_ia:-$DEF_IA}

# 6. BitTorrent (opcional para archivos pesados)
echo ""
read -p "¿Descargar ficheros grandes por Bittorrent? (s/N): " menu_torrent < /dev/tty
if [ "${menu_torrent,,}" == "s" ]; then USE_TORRENT=1; else USE_TORRENT=0; fi

echo ""
read -p "Todo listo. ¿Comenzar la instalación? (s/n): " confirm < /dev/tty
if [ "${confirm,,}" != "s" ]; then 
    log_err "Instalación cancelada."
fi

# Detectar el nombre correcto del directorio de Escritorio (Desktop/Escritorio)
if [ -d "$HOME/Escritorio" ]; then
    ESCRITORIO="$HOME/Escritorio"
else
    ESCRITORIO="$HOME/Desktop"
fi

BASE_DIR="$HOME/refugiOS"
log_info "Creando estructura de directorios en $BASE_DIR..."
mkdir -p "$BASE_DIR"/{Apps/versiones,Conocimiento/versiones,Mapas,IA/versiones,Bovedas,Scripts}
mkdir -p "$ESCRITORIO"

# ------------------------------------------------------------------------------
# 1. Resolución de Bloqueos de Paquetes e Instalación de Dependencias
# ------------------------------------------------------------------------------
# En entornos Live recién iniciados, hay procesos automáticos que pueden bloquear el gestor de paquetes.
log_info "Preparando el sistema para instalar nuevos paquetes..."
sudo systemctl stop unattended-upgrades 2>/dev/null || true
sudo dpkg --configure -a || true
sudo apt-get install -f -y < /dev/null || true
sudo apt-get update -y

log_info "Instalando herramientas base y de soporte (Bloque 1/3)..."
sudo apt-get install -y curl wget aria2 jq rsync < /dev/null

log_info "Instalando herramientas base y de soporte (Bloque 2/3)..."
sudo apt-get install -y flatpak cryptsetup epiphany-browser gedit xfce4-terminal < /dev/null

log_info "Instalando herramientas base y de soporte (Bloque 3/3)..."
sudo apt-get install -y syncthing libreoffice vlc evince < /dev/null

# Intentar instalar soporte de idioma (Ubuntu) sin fallar el script si no existe (Debian/RPi/etc)
log_info "Instalando soporte de idioma para distribuciones Ubuntu"
sudo apt-get install -y language-selector-common < /dev/null 2>/dev/null || true

# Intentar instalar soporte de idioma para el autodetectado y el elegido en el menú
log_info "Verificando paquetes de soporte de idiomas ($SYS_LANG y $WIKI_LANG)..."
for l in "$SYS_LANG" "$WIKI_LANG"; do
    lang_pkgs=$(check-language-support -l "$l" 2>/dev/null || echo "")
    if [ -n "$lang_pkgs" ]; then
        log_info "Instalando paquetes de idioma para '$l'..."
        sudo apt-get install -y $lang_pkgs < /dev/null || true
    fi
done

# ------------------------------------------------------------------------------
# 2. Aplicaciones (Kiwix Desktop)
# ------------------------------------------------------------------------------
log_info "Instalando Kiwix Desktop..."

    # NOTA TÉCNICA: Kiwix no adjunta sus binarios (assets) en la API de GitHub para la versión de Desktop.
    # Hacer una llamada a la API allí devuelve una lista vacía. Por tanto, raspamos su servidor oficial:
    KIWIX_FILE=$(curl -sL https://download.kiwix.org/release/kiwix-desktop/ | grep -o 'kiwix-desktop_x86_64_[0-9.-]*\.appimage' | sort -V | tail -n 1)

    if [ -z "$KIWIX_FILE" ]; then
        log_err "Fallo al localizar la versión de Kiwix en los servidores."
    fi

if [ -f "$BASE_DIR/Apps/versiones/$KIWIX_FILE" ] && [ "$FORCE" -eq 0 ]; then
    log_info "Kiwix Desktop ($KIWIX_FILE) ya existe. Omitiendo descarga."
else
    KIWIX_URL="https://download.kiwix.org/release/kiwix-desktop/${KIWIX_FILE}"
    log_info "Descargando: $KIWIX_FILE"
    wget -c "$KIWIX_URL" -O "$BASE_DIR/Apps/versiones/$KIWIX_FILE"
    chmod +x "$BASE_DIR/Apps/versiones/$KIWIX_FILE"
    log_success "Kiwix Desktop descargado con éxito."
fi
ln -sf "$BASE_DIR/Apps/versiones/$KIWIX_FILE" "$BASE_DIR/Apps/kiwix-desktop.appimage"

# ------------------------------------------------------------------------------
# 3. Base de Datos (Enciclopedias Offline)
# ------------------------------------------------------------------------------
log_info "Buscando las últimas enciclopedias disponibles..."

    LATEST_MED=""
    if [ "$DOWNLOAD_MED" -eq 1 ]; then
        log_info "Buscando la última versión de WikiMed..."
        LATEST_MED=$(curl -sL https://download.kiwix.org/zim/wikipedia/ | grep -o "wikipedia_${WIKI_LANG}_medicine_maxi_[0-9-]*\.zim" | sort -V | tail -n 1)
        [ -z "$LATEST_MED" ] && log_err "Fallo al localizar WikiMed para el idioma: $WIKI_LANG."
    fi

    LATEST_WIKI=""
    if [ "$DOWNLOAD_WIKI" -eq 1 ]; then
        log_info "Buscando la última versión de Wikipedia ($WIKI_TYPE)..."
        LATEST_WIKI=$(curl -sL https://download.kiwix.org/zim/wikipedia/ | grep -o "wikipedia_${WIKI_LANG}_${WIKI_TYPE}_[0-9-]*\.zim" | sort -V | tail -n 1)
        [ -z "$LATEST_WIKI" ] && log_err "Fallo al localizar Wikipedia para el idioma: $WIKI_LANG."
    fi

    LATEST_HOWTO=""
    if [ "$DOWNLOAD_HOWTO" -eq 1 ]; then
        log_info "Buscando la última versión de WikiHow..."
        LATEST_HOWTO=$(curl -sL https://mirrors.dotsrc.org/kiwix/archive/zim/wikihow/ | grep -o "wikihow_${WIKI_LANG}_maxi_[0-9-]*\.zim" | sort -V | tail -n 1 || echo "")
        [ -z "$LATEST_HOWTO" ] && log_err "No se pudo encontrar una versión de WikiHow para el idioma $WIKI_LANG."
    fi

# --- Descargas Efectivas ---

# 1. WikiMed
if [ "$DOWNLOAD_MED" -eq 1 ]; then
    if [ -f "$BASE_DIR/Conocimiento/versiones/$LATEST_MED" ] && [ "$FORCE" -eq 0 ]; then
        log_info "WikiMed ya existe. Omitiendo descarga."
    else
        if [ "$USE_TORRENT" -eq 1 ]; then
            log_info "Descargando WikiMed vía BitTorrent: $LATEST_MED"
            aria2c --seed-time=0 --continue=true --dir="$BASE_DIR/Conocimiento/versiones/" "https://download.kiwix.org/zim/wikipedia/${LATEST_MED}.torrent"
        else
            log_info "Descargando WikiMed: $LATEST_MED"
            aria2c -x 4 --continue=true --auto-file-renaming=false --dir="$BASE_DIR/Conocimiento/versiones/" -o "$LATEST_MED" "https://download.kiwix.org/zim/wikipedia/$LATEST_MED"
        fi
    fi
    ln -sf "$BASE_DIR/Conocimiento/versiones/$LATEST_MED" "$BASE_DIR/Conocimiento/wikimed.zim"
else
    log_info "Omitiendo WikiMed por elección del usuario."
    rm -f "$BASE_DIR/Conocimiento/wikimed.zim"
fi

# 2. Wikipedia Principal
if [ "$DOWNLOAD_WIKI" -eq 1 ]; then
    if [ -f "$BASE_DIR/Conocimiento/versiones/$LATEST_WIKI" ] && [ "$FORCE" -eq 0 ]; then
        log_info "Wikipedia Principal ya existe. Omitiendo descarga."
    else
        if [ "$USE_TORRENT" -eq 1 ]; then
            log_info "Descargando Wikipedia vía BitTorrent: $LATEST_WIKI"
            aria2c --seed-time=0 --continue=true --dir="$BASE_DIR/Conocimiento/versiones/" "https://download.kiwix.org/zim/wikipedia/${LATEST_WIKI}.torrent"
        else
            log_info "Descargando Wikipedia ($WIKI_TYPE): $LATEST_WIKI"
            aria2c -x 4 --continue=true --auto-file-renaming=false --dir="$BASE_DIR/Conocimiento/versiones/" -o "$LATEST_WIKI" "https://download.kiwix.org/zim/wikipedia/$LATEST_WIKI"
        fi
    fi
    ln -sf "$BASE_DIR/Conocimiento/versiones/$LATEST_WIKI" "$BASE_DIR/Conocimiento/wikipedia.zim"
else
    log_info "Omitiendo Wikipedia por elección del usuario."
    rm -f "$BASE_DIR/Conocimiento/wikipedia.zim"
fi

# 3. WikiHow
if [ "$DOWNLOAD_HOWTO" -eq 1 ]; then
    if [ -f "$BASE_DIR/Conocimiento/versiones/$LATEST_HOWTO" ] && [ "$FORCE" -eq 0 ]; then
        log_info "WikiHow ya existe. Omitiendo descarga."
    else
        log_info "Descargando WikiHow ($WIKI_LANG): $LATEST_HOWTO"
        aria2c -x 4 --continue=true --auto-file-renaming=false --dir="$BASE_DIR/Conocimiento/versiones/" -o "$LATEST_HOWTO" "https://mirrors.dotsrc.org/kiwix/archive/zim/wikihow/$LATEST_HOWTO"
    fi
    ln -sf "$BASE_DIR/Conocimiento/versiones/$LATEST_HOWTO" "$BASE_DIR/Conocimiento/wikihow.zim"
else
    log_info "Omitiendo WikiHow."
    rm -f "$BASE_DIR/Conocimiento/wikihow.zim"
fi


log_info "Creando lanzadores individuales para cada corpus de conocimiento..."
for zim in "$BASE_DIR/Conocimiento"/*.zim; do
    [ -e "$zim" ] || continue
    FILENAME=$(basename "$zim")
    case "$FILENAME" in
        wikipedia.zim) NAME="Wikipedia" ;;
        wikimed.zim)   NAME="WikiMed (Medicina)" ;;
        wikihow.zim)   NAME="WikiHow" ;;
        *) NAME=$(echo "$FILENAME" | sed 's/\.zim$//; s/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1') ;;
    esac

    cat << EOF > "$ESCRITORIO/Conocimiento_${NAME// /_}.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=$NAME (Offline)
Comment=Acceso directo a $NAME
Exec=$BASE_DIR/Apps/kiwix-desktop.appimage $zim
Icon=accessories-dictionary
Terminal=false
EOF
    chmod +x "$ESCRITORIO/Conocimiento_${NAME// /_}.desktop"
done
log_success "Corpus de conocimiento garantizado."

# ------------------------------------------------------------------------------
# 4. Módulo Cartográfico Offline
# ------------------------------------------------------------------------------
log_info "Instalando motor cartográfico Organic Maps..."
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo < /dev/null
sudo flatpak install flathub app.organicmaps.desktop -y < /dev/null

# Asegurar acceso a la GPU (aunque el lanzador falle, dejamos el permiso)
[ "$IS_RPI" -eq 1 ] && sudo flatpak override --device=dri app.organicmaps.desktop || true

cat << EOF > "$ESCRITORIO/Mapas_Offline.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Mapas GPS (Organic Maps)
Exec=flatpak run app.organicmaps.desktop
Icon=app.organicmaps.desktop
Terminal=false
EOF
chmod +x "$ESCRITORIO/Mapas_Offline.desktop"

# ------------------------------------------------------------------------------
# 5. Inteligencia Artificial Residente (Niveles de Razonamiento)
# ------------------------------------------------------------------------------
if [ "$menu_ia" == "1" ] || [ "$menu_ia" == "2" ]; then
    log_info "Preparando el asistente de Inteligencia Artificial..."
 
    # --- Motor de Inferencia (Llamafile) ---
    LLAMAFILE_URL=$(curl -sL https://api.github.com/repos/Mozilla-Ocho/llamafile/releases/latest | jq -r '.assets[].browser_download_url' | grep -E 'llamafile-[0-9.]+$' | head -n 1)
 
    if [ -z "$LLAMAFILE_URL" ] || [ "$LLAMAFILE_URL" == "null" ]; then
        log_err "No se pudo encontrar el enlace de descarga de la IA."
    fi
    LLAMA_FILE=$(basename "$LLAMAFILE_URL")

    if [ -f "$BASE_DIR/IA/versiones/$LLAMA_FILE" ] && [ "$FORCE" -eq 0 ]; then
        log_info "El motor de IA ya está descargado ($LLAMA_FILE)."
    else
        log_info "Descargando motor de IA (Llamafile)..."
        wget -c "$LLAMAFILE_URL" -O "$BASE_DIR/IA/versiones/$LLAMA_FILE"
        chmod +x "$BASE_DIR/IA/versiones/$LLAMA_FILE"
    fi
    ln -sf "$BASE_DIR/IA/versiones/$LLAMA_FILE" "$BASE_DIR/IA/llamafile"

    # --- Nivel 🟢 Básico: Phi-4-mini (3.8B, ~2.5 GB) - Siempre se descarga ---
    PHI4_FILE="microsoft_Phi-4-mini-instruct-Q4_K_M.gguf"
    if [ -f "$BASE_DIR/IA/versiones/$PHI4_FILE" ] && [ "$FORCE" -eq 0 ]; then
        log_info "Modelo básico (Phi-4-mini) ya existe. Omitiendo."
    else
        log_info "Descargando modelo básico: Phi-4-mini (~2.5 GB)..."
        wget -c "https://huggingface.co/bartowski/microsoft_Phi-4-mini-instruct-GGUF/resolve/main/$PHI4_FILE" -O "$BASE_DIR/IA/versiones/$PHI4_FILE"
    fi
    ln -sf "$BASE_DIR/IA/versiones/$PHI4_FILE" "$BASE_DIR/IA/modelo-basico.gguf"

    # --- Niveles adicionales (solo pack completo) ---
    if [ "$menu_ia" == "2" ]; then
        # Nivel 🟡 Medio: Qwen3-8B (~5 GB)
        QWEN8_FILE="Qwen_Qwen3-8B-Q4_K_M.gguf"
        if [ -f "$BASE_DIR/IA/versiones/$QWEN8_FILE" ] && [ "$FORCE" -eq 0 ]; then
            log_info "Modelo medio (Qwen3-8B) ya existe. Omitiendo."
        else
            log_info "Descargando modelo medio: Qwen3-8B (~5 GB)..."
            wget -c "https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF/resolve/main/$QWEN8_FILE" -O "$BASE_DIR/IA/versiones/$QWEN8_FILE"
        fi
        ln -sf "$BASE_DIR/IA/versiones/$QWEN8_FILE" "$BASE_DIR/IA/modelo-medio.gguf"

        # Nivel 🔴 Avanzado: Qwen3-14B (~9 GB)
        QWEN14_FILE="Qwen_Qwen3-14B-Q4_K_M.gguf"
        if [ -f "$BASE_DIR/IA/versiones/$QWEN14_FILE" ] && [ "$FORCE" -eq 0 ]; then
            log_info "Modelo avanzado (Qwen3-14B) ya existe. Omitiendo."
        else
            log_info "Descargando modelo avanzado: Qwen3-14B (~9 GB)..."
            wget -c "https://huggingface.co/bartowski/Qwen_Qwen3-14B-GGUF/resolve/main/$QWEN14_FILE" -O "$BASE_DIR/IA/versiones/$QWEN14_FILE"
        fi
        ln -sf "$BASE_DIR/IA/versiones/$QWEN14_FILE" "$BASE_DIR/IA/modelo-avanzado.gguf"
    fi

    # --- Script selector de modelo según RAM disponible ---
    cat << 'SELECTOR_EOF' > "$BASE_DIR/Scripts/refugios-ia-selector.sh"
#!/bin/bash
# ============================================
# Selector de Modelo de IA - refugiOS
# Detecta la RAM y elige el modelo adecuado
# ============================================
IA_DIR="$HOME/refugiOS/IA"

# Detectar RAM total en MB
RAM_MB=$(free -m | awk '/^Mem:/{print $2}')

# Verificar qué modelos están disponibles
TIENE_AVANZADO=0; TIENE_MEDIO=0; TIENE_BASICO=0
[ -f "$IA_DIR/modelo-avanzado.gguf" ] && TIENE_AVANZADO=1
[ -f "$IA_DIR/modelo-medio.gguf" ]    && TIENE_MEDIO=1
[ -f "$IA_DIR/modelo-basico.gguf" ]   && TIENE_BASICO=1

# Si solo hay un modelo, usarlo directamente
MODELOS_DISPONIBLES=$((TIENE_BASICO + TIENE_MEDIO + TIENE_AVANZADO))
if [ "$MODELOS_DISPONIBLES" -eq 1 ]; then
    if [ "$TIENE_AVANZADO" -eq 1 ]; then MODELO="modelo-avanzado.gguf"; NOMBRE="Avanzado (Qwen3-14B)"
    elif [ "$TIENE_MEDIO" -eq 1 ];   then MODELO="modelo-medio.gguf";   NOMBRE="Medio (Qwen3-8B)"
    else                                   MODELO="modelo-basico.gguf";  NOMBRE="Básico (Phi-4-mini)"
    fi
    echo "Modelo único detectado: $NOMBRE"
else
    # Autoselección según RAM
    if [ "$RAM_MB" -ge 14000 ] && [ "$TIENE_AVANZADO" -eq 1 ]; then
        RECOMENDADO="3"; REC_NOMBRE="Avanzado (Qwen3-14B)"
    elif [ "$RAM_MB" -ge 7000 ] && [ "$TIENE_MEDIO" -eq 1 ]; then
        RECOMENDADO="2"; REC_NOMBRE="Medio (Qwen3-8B)"
    else
        RECOMENDADO="1"; REC_NOMBRE="Básico (Phi-4-mini)"
    fi

    echo ""
    echo "=== SELECTOR DE MODELO DE IA ==="
    echo "RAM detectada: ${RAM_MB} MB"
    echo ""
    [ "$TIENE_BASICO" -eq 1 ]   && echo "  1) 🟢 Básico   - Phi-4-mini  (necesita ~4 GB RAM)"
    [ "$TIENE_MEDIO" -eq 1 ]    && echo "  2) 🟡 Medio    - Qwen3-8B    (necesita ~8 GB RAM)"
    [ "$TIENE_AVANZADO" -eq 1 ] && echo "  3) 🔴 Avanzado - Qwen3-14B   (necesita ~16 GB RAM)"
    echo ""
    read -p "Elige modelo [Enter para recomendado: $REC_NOMBRE]: " ELECCION < /dev/tty
    ELECCION=${ELECCION:-$RECOMENDADO}

    case "$ELECCION" in
        3) MODELO="modelo-avanzado.gguf"; NOMBRE="Avanzado (Qwen3-14B)" ;;
        2) MODELO="modelo-medio.gguf";    NOMBRE="Medio (Qwen3-8B)" ;;
        *) MODELO="modelo-basico.gguf";   NOMBRE="Básico (Phi-4-mini)" ;;
    esac
    echo "Lanzando modelo: $NOMBRE"
fi

# Ajuste de contexto para evitar fallos de memoria (Phi-4 y otros)
# Un contexto de 4096 es seguro para equipos con 4GB-12GB de RAM.
cd "$IA_DIR"
./llamafile -m "$MODELO" --ctx-size 4096 --server &
LLAMA_PID=$!
sleep 5
epiphany-browser http://localhost:8080 2>/dev/null || xdg-open http://localhost:8080 2>/dev/null
echo ""
echo "El asistente de IA está corriendo. Cierra esta ventana para detenerlo."
wait $LLAMA_PID
SELECTOR_EOF
    chmod +x "$BASE_DIR/Scripts/refugios-ia-selector.sh"

    # --- Lanzador de escritorio ---
    cat << EOF > "$ESCRITORIO/Asistente_IA.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Asistente IA
Comment=Selecciona y lanza el modelo de IA adecuado
Exec=xfce4-terminal -e "$BASE_DIR/Scripts/refugios-ia-selector.sh"
Icon=utilities-terminal
Terminal=false
EOF
    chmod +x "$ESCRITORIO/Asistente_IA.desktop"
    log_success "Asistente de IA configurado con $([ "$menu_ia" == "2" ] && echo "3 niveles" || echo "modelo básico")."
else
    log_info "Instalación de IA omitida."
fi

# ------------------------------------------------------------------------------
# 6. Bóveda Segura (Datos cifrados)
# ------------------------------------------------------------------------------
log_info "Configurando herramientas para la Bóveda Segura..."

# NOTA: Usamos comillas simples 'EOF' para evitar la expansión de las variables del usuario
# antes de que se creen los scripts internos.

cat << 'EOF' > "$BASE_DIR/Scripts/refugios-vault-create.sh"
#!/bin/bash
set -e
FILE="$HOME/refugiOS/Bovedas/datos_personales.img"
echo "--- GENERANDO BÓVEDA SEGURA ---"
echo "Se creará un contenedor criptográfico preasignado de 3 GB."
dd if=/dev/urandom of="$FILE" bs=1M count=3072 status=progress
echo "Inicializando cifrado. Teclea YES en mayúsculas cuando se solicite."
echo "Después se solicitará varias veces la contraseña que protegerá el sistema."
sudo cryptsetup luksFormat "$FILE"
echo "Desbloqueando bóveda para formateo interno..."
sudo cryptsetup open "$FILE" boveda_activa
sudo mkfs.ext4 /dev/mapper/boveda_activa
sudo cryptsetup close boveda_activa
echo "======================================"
echo "BÓVEDA CREADA Y SELLADA EXITOSAMENTE."
echo "Puedes cerrar esta ventana."
echo "======================================"
sleep 5
EOF

cat << 'EOF' > "$BASE_DIR/Scripts/refugios-vault-open.sh"
#!/bin/bash
set -e
FILE="$HOME/refugiOS/Bovedas/datos_personales.img"

if [ -d "$HOME/Escritorio" ]; then DIR="$HOME/Escritorio/MIS_DATOS_SECRETOS"
else DIR="$HOME/Desktop/MIS_DATOS_SECRETOS"; fi

mkdir -p "$DIR"
echo "Introduce tu contraseña para desbloquear la bóveda:"
sudo cryptsetup open "$FILE" boveda_activa
sudo mount /dev/mapper/boveda_activa "$DIR"
sudo chown -R $USER:$USER "$DIR"
echo "Bóveda montada correctamente en el escritorio. Puedes minimizar esta ventana."
sleep 3
EOF

cat << 'EOF' > "$BASE_DIR/Scripts/refugios-vault-close.sh"
#!/bin/bash
if [ -d "$HOME/Escritorio" ]; then DIR="$HOME/Escritorio/MIS_DATOS_SECRETOS"
else DIR="$HOME/Desktop/MIS_DATOS_SECRETOS"; fi

sudo umount "$DIR" || true
sudo cryptsetup close boveda_activa || true
rmdir "$DIR" || true
echo "La Bóveda ha sido sellada y borrada de la memoria."
sleep 3
EOF

chmod +x "$BASE_DIR/Scripts/"*.sh

# Inyección de lanzadores gráficos
cat << EOF > "$ESCRITORIO/1_Crear_Boveda.desktop"
[Desktop Entry]
Type=Application
Name=1. Inicializar Bóveda (Una sola vez)
Exec=xfce4-terminal -e "$BASE_DIR/Scripts/refugios-vault-create.sh"
Icon=dialog-password
Terminal=false
EOF

cat << EOF > "$ESCRITORIO/2_Abrir_Boveda.desktop"
[Desktop Entry]
Type=Application
Name=2. Desbloquear Bóveda
Exec=xfce4-terminal -e "$BASE_DIR/Scripts/refugios-vault-open.sh"
Icon=folder-open
Terminal=false
EOF

cat << EOF > "$ESCRITORIO/3_Cerrar_Boveda.desktop"
[Desktop Entry]
Type=Application
Name=3. Sellar Bóveda
Exec=xfce4-terminal -e "$BASE_DIR/Scripts/refugios-vault-close.sh"
Icon=system-lock-screen
Terminal=false
EOF

chmod +x "$ESCRITORIO"/*.desktop
# Marcar como confiables en entornos como LXDE (Raspberry Pi OS) / XFCE
if command -v gio >/dev/null 2>&1; then
    log_info "Certificando lanzadores del escritorio..."
    for f in "$ESCRITORIO"/*.desktop; do
        gio set "$f" metadata::trusted yes 2>/dev/null || true
        # Para XFCE, es necesario el checksum para evitar el aviso de "Lanzador no confiable"
        checksum=$(sha256sum "$f" | awk '{print $1}')
        gio set "$f" metadata::xfce-exe-checksum "$checksum" 2>/dev/null || true
    done
fi

# Intentar desactivar el aviso "Execute File" de PCManFM (Raspberry Pi OS / LXDE)
LIBFM_CONFIG="$HOME/.config/libfm/libfm.conf"
if [ -f "$LIBFM_CONFIG" ]; then
    if grep -q "quick_exec=" "$LIBFM_CONFIG"; then
        sed -i 's/quick_exec=0/quick_exec=1/' "$LIBFM_CONFIG"
    else
        sed -i '/\[General\]/a quick_exec=1' "$LIBFM_CONFIG" 2>/dev/null || echo -e "[General]\nquick_exec=1" >> "$LIBFM_CONFIG"
    fi
fi

# 7. Diagnóstico de Persistencia (Advertencia Segura)
# ------------------------------------------------------------------------------
if [ "$IS_RPI" -eq 0 ] && ! grep -q "persistent" /proc/cmdline; then
    echo -e "\n\e[1;33m[!] ADVERTENCIA DE PERSISTENCIA:\e[0m"
    echo "Se ha detectado que el sistema NO está corriendo con el flag 'persistent'."
    echo "Si estás en un Live USB, tus cambios se perderán al reiniciar."
    echo "Consulta la documentación del proyecto para saber cómo activar la"
    echo "persistencia permanente en el menú de arranque (GRUB)."
    echo ""
    sleep 2
fi

echo "============================================================"
echo "  INSTALACIÓN COMPLETA. Verifica tu escritorio."
echo "  "
echo "  Es aconsejable lanzar cada aplicación al menos una vez"
echo "  para que se creen sus configuraciones antes de dar el"
echo "  dispositivo por cerrado."
echo "  "
echo "  En concreto, se aconseja descargar todos los mapas offline"
echo "  que se puedan necesitar."
echo "  "
echo "  A partir de ese momento podrás usarlo desconectado."
echo "============================================================"
