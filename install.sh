#!/bin/bash
# ============================================
# refugiOS - Script de Ensamblaje Táctico 
# (versión de prueba para unidades de 32 GB)
# ============================================

# Detener la ejecución si hay errores críticos o variables sin definir
set -euo pipefail

# Funciones de color para un log limpio y legible
log_info() { echo -e "\e[1;34m[*]\e[0m $1"; }
log_err()  { echo -e "\e[1;31m[X] ERROR:\e[0m $1"; exit 1; }
log_success() { echo -e "\e[1;32m[v] ÉXITO:\e[0m $1"; }

# ============================================
# Argumentos
# ============================================
FORCE=0
for arg in "$@"; do
    if [ "$arg" == "--force" ]; then
        FORCE=1
        log_info "Modo --force activado. Se sobrescribirán las descargas existentes."
    fi
done

# ============================================
# Detección de recursos y validación
# ============================================
# Detectar idioma (basado en LANG, asumiendo 'es' por defecto)
SYS_LANG=$(echo "${LANG:-es}" | cut -d'_' -f1)
log_info "Idioma detectado para el sistema: $SYS_LANG"

# Detectar el tamaño del sistema de ficheros raíz (/) en MB
TOTAL_MB=$(df -m / | awk 'NR==2 {print $2}')
FREE_MB=$(df -m / | awk 'NR==2 {print $4}')

log_info "Espacio total asignado en raíz: ${TOTAL_MB} MB. Libre: ${FREE_MB} MB."

if [ "$TOTAL_MB" -lt 15000 ]; then
    echo -e "\e[1;33m[!] ADVERTENCIA: Se ha detectado un tamaño de disco muy pequeño (menos de 15 GB asignados).\e[0m"
    echo "Es probable que estés ejecutando este Live USB sin haber creado una imagen permanente"
    echo "asignando todo el disco disponible como espacio libre, o te faltó usar 'persistent'."
    echo "Puedes experimentar fallos de despacio con bases de datos grandes."
    echo "Revisa la Guía de Ensamblaje en el README."
    read -p "¿Deseas continuar bajo tu propio riesgo? (s/n): " confirm_space < /dev/tty
    if [ "$confirm_space" != "s" ] && [ "$confirm_space" != "S" ]; then 
        log_err "Instalación cancelada para ajustar el tamaño del disco."
    fi
fi

read -p "Este script preparará tu sistema. ¿Continuar? (s/n): " confirm < /dev/tty
if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then 
    log_err "Instalación cancelada por el usuario."
fi

# Detectar el nombre correcto del directorio de Escritorio (Desktop/Escritorio)
if [ -d "$HOME/Escritorio" ]; then
    ESCRITORIO="$HOME/Escritorio"
else
    ESCRITORIO="$HOME/Desktop"
fi

BASE_DIR="$HOME/refugiOS"
log_info "Creando estructura de directorios en $BASE_DIR..."
mkdir -p "$BASE_DIR"/{Apps,Conocimiento,Mapas,IA,Bovedas,Scripts}
mkdir -p "$ESCRITORIO"

# ------------------------------------------------------------------------------
# 1. Resolución de Bloqueos de Paquetes e Instalación de Dependencias
# ------------------------------------------------------------------------------
# En entornos Live recién iniciados, 'unattended-upgrades' a menudo bloquea apt.
log_info "Neutralizando bloqueos automáticos de dpkg/apt..."
sudo systemctl stop unattended-upgrades 2>/dev/null || true
sudo dpkg --configure -a || true
sudo apt-get install -f -y < /dev/null || true

log_info "Instalando dependencias críticas y paquetes de soporte de idioma local..."
sudo apt-get update -y
sudo apt-get install -y curl wget aria2 jq flatpak cryptsetup rsync language-selector-common < /dev/null

lang_pkgs=$(check-language-support -l "$SYS_LANG" 2>/dev/null || echo "")
if [ -n "$lang_pkgs" ]; then
    log_info "Instalando los paquetes de idioma para $SYS_LANG..."
    sudo apt-get install -y $lang_pkgs < /dev/null || true
fi

# ------------------------------------------------------------------------------
# 2. Descarga de Kiwix Desktop (AppImage)
# ------------------------------------------------------------------------------
log_info "Extrayendo el binario más reciente de Kiwix Desktop..."

if [ -f "$BASE_DIR/Apps/kiwix-desktop.appimage" ] && [ "$FORCE" -eq 0 ]; then
    log_info "Kiwix Desktop ya existe. Omitiendo descarga (usa --force para forzar)."
else
    # NOTA TÉCNICA: Kiwix no adjunta sus binarios (assets) en la API de GitHub para la versión de Desktop.
    # Hacer una llamada a la API allí devuelve una lista vacía. Por tanto, raspamos su servidor oficial:
    KIWIX_FILE=$(curl -sL https://download.kiwix.org/release/kiwix-desktop/ | grep -o 'kiwix-desktop_x86_64_[0-9.-]*\.appimage' | sort -V | tail -n 1)

    if [ -z "$KIWIX_FILE" ]; then
        log_err "Fallo al localizar la versión de Kiwix en los servidores."
    fi

    KIWIX_URL="https://download.kiwix.org/release/kiwix-desktop/${KIWIX_FILE}"
    log_info "Descargando: $KIWIX_FILE"
    wget -c "$KIWIX_URL" -O "$BASE_DIR/Apps/kiwix-desktop.appimage"
    chmod +x "$BASE_DIR/Apps/kiwix-desktop.appimage"
    log_success "Kiwix Desktop instalado con éxito."
fi

# ------------------------------------------------------------------------------
# 3. Base de Datos Desconectada (Archivos ZIM)
# ------------------------------------------------------------------------------
log_info "Rastreando enciclopedias en español actualizadas..."

if [ -f "$BASE_DIR/Conocimiento/wikimed.zim" ] && [ -f "$BASE_DIR/Conocimiento/wikipedia.zim" ] && [ "$FORCE" -eq 0 ]; then
    log_info "Enciclopedias ZIM ya existen. Omitiendo descarga conjunta (usa --force para forzar)."
else
    LATEST_MED=$(curl -sL https://download.kiwix.org/zim/wikipedia/ | grep -o 'wikipedia_es_medicine_maxi_[0-9-]*\.zim' | sort -V | tail -n 1)
    LATEST_WIKI_NOPIC=$(curl -sL https://download.kiwix.org/zim/wikipedia/ | grep -o 'wikipedia_es_top_mini_[0-9-]*\.zim' | sort -V | tail -n 1)

    if [ -z "$LATEST_MED" ] || [ -z "$LATEST_WIKI_NOPIC" ]; then
        log_err "Los repositorios ZIM de Kiwix no respondieron como se esperaba."
    fi

    log_info "Descargando WikiMed: $LATEST_MED (~2GB)"
    aria2c -x 4 --dir="$BASE_DIR/Conocimiento/" -o "wikimed.zim" "https://download.kiwix.org/zim/wikipedia/$LATEST_MED"

    log_info "Descargando Wikipedia (Top Mini - Pruebas): $LATEST_WIKI_NOPIC (~183MB)"
    aria2c -x 4 --dir="$BASE_DIR/Conocimiento/" -o "wikipedia.zim" "https://download.kiwix.org/zim/wikipedia/$LATEST_WIKI_NOPIC"
fi

cat << EOF > "$ESCRITORIO/Conocimiento_Offline.desktop"

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
log_info "Resolviendo dependencias del Motor de IA Llamafile..."

if [ -f "$BASE_DIR/IA/llamafile" ] && [ "$FORCE" -eq 0 ]; then
    log_info "Motor de IA Llamafile ya existe. Omitiendo descarga."
else
    # En este caso sí usamos la API de GitHub combinada con grep nativo para evadir fallos de compatibilidad en JQ
    LLAMAFILE_URL=$(curl -sL https://api.github.com/repos/Mozilla-Ocho/llamafile/releases/latest | jq -r '.assets[].browser_download_url' | grep -E 'llamafile-[0-9.]+$' | head -n 1)

    if [ -z "$LLAMAFILE_URL" ] || [ "$LLAMAFILE_URL" == "null" ]; then
        log_err "No se pudo resolver la URL del ejecutable de Llamafile."
    fi

    log_info "Descargando Llamafile Engine..."
    wget -c "$LLAMAFILE_URL" -O "$BASE_DIR/IA/llamafile"
    chmod +x "$BASE_DIR/IA/llamafile"
fi

if [ -f "$BASE_DIR/IA/Phi-3.5-mini.gguf" ] && [ "$FORCE" -eq 0 ]; then
    log_info "Modelo cognitivo Phi-3.5 Mini ya existe. Omitiendo descarga."
else
    log_info "Descargando modelo cognitivo Phi-3.5 Mini (Altamente Optimizado)..."
    wget -c "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf" -O "$BASE_DIR/IA/Phi-3.5-mini.gguf"
fi

cat << EOF > "$ESCRITORIO/Asistente_IA.desktop"

Version=1.0
Type=Application
Name=Asistente IA de Supervivencia
Comment=Lanza el LLM y abre el navegador
Exec=bash -c "cd $BASE_DIR/IA &&./llamafile -m Phi-3.5-mini.gguf --server & sleep 5 && xdg-open http://localhost:8080"
Icon=utilities-terminal
Terminal=true
EOF
chmod +x "$ESCRITORIO/Asistente_IA.desktop"
log_success "Motor de IA configurado."

# ------------------------------------------------------------------------------
# 6. Forjado del Santuario Criptográfico (LUKS)
# ------------------------------------------------------------------------------
log_info "Generando rutinas lógicas para Bóveda Criptográfica..."

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

Type=Application
Name=1. Inicializar Bóveda (Una sola vez)
Exec=lxterminal -e "$BASE_DIR/Scripts/refugios-vault-create.sh"
Icon=dialog-password
Terminal=false
EOF

cat << EOF > "$ESCRITORIO/2_Abrir_Boveda.desktop"

Type=Application
Name=2. Desbloquear Bóveda
Exec=lxterminal -e "$BASE_DIR/Scripts/refugios-vault-open.sh"
Icon=folder-open
Terminal=false
EOF

cat << EOF > "$ESCRITORIO/3_Cerrar_Boveda.desktop"

Type=Application
Name=3. Sellar Bóveda
Exec=lxterminal -e "$BASE_DIR/Scripts/refugios-vault-close.sh"
Icon=system-lock-screen
Terminal=false
EOF

chmod +x "$ESCRITORIO"/*.desktop

echo "============================================================"
echo " EXCELENTE: Instalación Completa. Verifica tu escritorio."
echo "============================================================"
