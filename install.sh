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

log_info "Espacio asignado en raíz: ${TOTAL_MB} MB. Libre: ${FREE_MB} MB."

# Autoselección según capacidad (menor a 25GB -> modo Lite)
if [ "$TOTAL_MB" -lt 25000 ]; then
    DEF_WIKI="2" # Top Mini
    DEF_IA="2"   # Omitir IA
    log_info "Capacidad reducida detectada. Se recomendarán versiones ligeras."
else
    DEF_WIKI="1" # All NoPic
    DEF_IA="1"   # Incluir IA
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

# 3. Tamaño Wikipedia
echo ""
echo "¿Qué versión de la Wikipedia deseas descargar?"
echo "  1) Completa sin imágenes (~11 GB)"
echo "  2) Top Mini (~200 MB)"
read -p "Opción [1-2] (Enter para la recomendada: $DEF_WIKI): " menu_wiki < /dev/tty
menu_wiki=${menu_wiki:-$DEF_WIKI}
if [ "$menu_wiki" == "1" ]; then
    WIKI_TYPE="all_nopic"
else
    WIKI_TYPE="top_mini"
fi

# 4. Inteligencia Artificial
echo ""
echo "¿Deseas descargar el motor de Inteligencia Artificial Phi-3.5 (~2.4 GB)?"
echo "  1) Sí"
echo "  2) No, omitir IA"
read -p "Opción [1-2] (Enter para la recomendada: $DEF_IA): " menu_ia < /dev/tty
menu_ia=${menu_ia:-$DEF_IA}

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
 
log_info "Instalando herramientas base y de soporte..."
sudo apt-get update -y
sudo apt-get install -y curl wget aria2 jq flatpak cryptsetup rsync language-selector-common < /dev/null

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

    LATEST_MED=$(curl -sL https://download.kiwix.org/zim/wikipedia/ | grep -o "wikipedia_${WIKI_LANG}_medicine_maxi_[0-9-]*\.zim" | sort -V | tail -n 1)
    LATEST_WIKI=$(curl -sL https://download.kiwix.org/zim/wikipedia/ | grep -o "wikipedia_${WIKI_LANG}_${WIKI_TYPE}_[0-9-]*\.zim" | sort -V | tail -n 1)

    if [ -z "$LATEST_MED" ] || [ -z "$LATEST_WIKI" ]; then
        log_err "Fallo al localizar las enciclopedias ZIM para el idioma seleccionado: $WIKI_LANG."
    fi

if [ -f "$BASE_DIR/Conocimiento/versiones/$LATEST_MED" ] && [ -f "$BASE_DIR/Conocimiento/versiones/$LATEST_WIKI" ] && [ "$FORCE" -eq 0 ]; then
    log_info "Enciclopedias ZIM ya existen en versiones. Omitiendo la descarga."
else
    log_info "Descargando WikiMed: $LATEST_MED"
    aria2c -x 4 --dir="$BASE_DIR/Conocimiento/versiones/" -o "$LATEST_MED" "https://download.kiwix.org/zim/wikipedia/$LATEST_MED"

    log_info "Descargando Wikipedia Principal ($WIKI_TYPE): $LATEST_WIKI"
    aria2c -x 4 --dir="$BASE_DIR/Conocimiento/versiones/" -o "$LATEST_WIKI" "https://download.kiwix.org/zim/wikipedia/$LATEST_WIKI"
fi
ln -sf "$BASE_DIR/Conocimiento/versiones/$LATEST_MED" "$BASE_DIR/Conocimiento/wikimed.zim"
ln -sf "$BASE_DIR/Conocimiento/versiones/$LATEST_WIKI" "$BASE_DIR/Conocimiento/wikipedia.zim"

cat << EOF > "$ESCRITORIO/Conocimiento_Offline.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Conocimiento Offline (Kiwix)
Comment=Acceso a Wikipedia y WikiMed
Exec=$BASE_DIR/Apps/kiwix-desktop.appimage
Icon=accessories-dictionary
Terminal=false
EOF
chmod +x "$ESCRITORIO/Conocimiento_Offline.desktop"
log_success "Corpus de conocimiento garantizado."

# ------------------------------------------------------------------------------
# 4. Módulo Cartográfico Offline
# ------------------------------------------------------------------------------
log_info "Instalando motor cartográfico Organic Maps..."
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo < /dev/null
sudo flatpak install flathub app.organicmaps.desktop -y < /dev/null

cat << EOF > "$ESCRITORIO/Mapas_Offline.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Mapas GPS (Organic Maps)
Exec=flatpak run app.organicmaps.desktop
Icon=browser
Terminal=false
EOF
chmod +x "$ESCRITORIO/Mapas_Offline.desktop"

# ------------------------------------------------------------------------------
# 5. Inteligencia Artificial Residente
# ------------------------------------------------------------------------------
if [ "$menu_ia" == "1" ]; then
    log_info "Preparando el asistente de Inteligencia Artificial..."
 
    # Buscamos la descarga más reciente del motor Llamafile
    LLAMAFILE_URL=$(curl -sL https://api.github.com/repos/Mozilla-Ocho/llamafile/releases/latest | jq -r '.assets[].browser_download_url' | grep -E 'llamafile-[0-9.]+$' | head -n 1)
 
    if [ -z "$LLAMAFILE_URL" ] || [ "$LLAMAFILE_URL" == "null" ]; then
        log_err "No se pudo encontrar el enlace de descarga de la IA."
    fi
    LLAMA_FILE=$(basename "$LLAMAFILE_URL")

    if [ -f "$BASE_DIR/IA/versiones/$LLAMA_FILE" ] && [ "$FORCE" -eq 0 ]; then
        log_info "El motor de IA ya está descargado ($LLAMA_FILE)."
    else
        log_info "Descargando motor de IA..."
        wget -c "$LLAMAFILE_URL" -O "$BASE_DIR/IA/versiones/$LLAMA_FILE"
        chmod +x "$BASE_DIR/IA/versiones/$LLAMA_FILE"
    fi
    ln -sf "$BASE_DIR/IA/versiones/$LLAMA_FILE" "$BASE_DIR/IA/llamafile"

    PHI_FILE="Phi-3.5-mini-instruct-Q4_K_M.gguf"
    if [ -f "$BASE_DIR/IA/versiones/$PHI_FILE" ] && [ "$FORCE" -eq 0 ]; then
        log_info "El modelo de lenguaje ya existe. Omitiendo."
    else
        log_info "Descargando modelo de lenguaje Phi-3.5..."
        wget -c "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/$PHI_FILE" -O "$BASE_DIR/IA/versiones/$PHI_FILE"
    fi
    ln -sf "$BASE_DIR/IA/versiones/$PHI_FILE" "$BASE_DIR/IA/Phi-3.5-mini.gguf"

    cat << EOF > "$ESCRITORIO/Asistente_IA.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Asistente IA de Supervivencia
Comment=Lanza el LLM y abre el navegador
Exec=bash -c "cd $BASE_DIR/IA &&./llamafile -m Phi-3.5-mini.gguf --server & sleep 5 && xdg-open http://localhost:8080"
Icon=utilities-terminal
Terminal=false
EOF
    chmod +x "$ESCRITORIO/Asistente_IA.desktop"
    log_success "Asistente de IA configurado."
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
dd if=/dev/zero of="$FILE" bs=1M count=3072 status=progress
echo "Inicializando cifrado. SE TE PEDIRÁ UNA NUEVA CONTRASEÑA EN MAYÚSCULAS."
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
Exec=lxterminal -e "$BASE_DIR/Scripts/refugios-vault-create.sh"
Icon=dialog-password
Terminal=false
EOF

cat << EOF > "$ESCRITORIO/2_Abrir_Boveda.desktop"
[Desktop Entry]
Type=Application
Name=2. Desbloquear Bóveda
Exec=lxterminal -e "$BASE_DIR/Scripts/refugios-vault-open.sh"
Icon=folder-open
Terminal=false
EOF

cat << EOF > "$ESCRITORIO/3_Cerrar_Boveda.desktop"
[Desktop Entry]
Type=Application
Name=3. Sellar Bóveda
Exec=lxterminal -e "$BASE_DIR/Scripts/refugios-vault-close.sh"
Icon=system-lock-screen
Terminal=false
EOF

chmod +x "$ESCRITORIO"/*.desktop
# Marcar como confiables en entornos como XFCE/MATE/GNOME para evitar la advertencia de "Untrusted launcher"
if command -v gio >/dev/null 2>&1; then
    for f in "$ESCRITORIO"/*.desktop; do
        gio set "$f" metadata::trusted yes 2>/dev/null || true
    done
fi

# ------------------------------------------------------------------------------
# 7. Diagnóstico de Persistencia (Advertencia Segura)
# ------------------------------------------------------------------------------
if ! grep -q "persistent" /proc/cmdline; then
    echo -e "\n\e[1;33m[!] ADVERTENCIA DE PERSISTENCIA:\e[0m"
    echo "Se ha detectado que el sistema NO está corriendo con el flag 'persistent'."
    echo "Si estás en un Live USB, tus cambios se perderán al reiniciar."
    echo "Consulta la documentación del proyecto para saber cómo activar la"
    echo "persistencia permanente en el menú de arranque (GRUB)."
    echo ""
    sleep 2
fi

echo "============================================================"
echo " EXCELENTE: Instalación Completa. Verifica tu escritorio."
echo "============================================================"
