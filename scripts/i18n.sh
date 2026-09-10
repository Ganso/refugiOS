#!/bin/bash
# refugiOS - Localization System (Bash)

# Default language
REFUGIOS_LANG="en"

# Load persistent language from config file. The user's explicit choice always wins.
LANG_CONFIG="$HOME/.refugios_lang"
PERSISTED_LANG=""
if [ -s "$LANG_CONFIG" ]; then
    PERSISTED_LANG=$(tr -d '[:space:]' < "$LANG_CONFIG")
fi

if [[ "$PERSISTED_LANG" == "es" || "$PERSISTED_LANG" == "en" ]]; then
    REFUGIOS_LANG="$PERSISTED_LANG"
elif [ -n "${LANG:-}" ]; then
    # Autodetection from the environment, only until a language has been persisted
    DETECTED_LANG=$(echo "$LANG" | cut -d'_' -f1 | tr '[:upper:]' '[:lower:]')
    if [[ "$DETECTED_LANG" == "es" || "$DETECTED_LANG" == "en" ]]; then
        REFUGIOS_LANG="$DETECTED_LANG"
    fi
fi

# ==============================================================================
# TRANSLATIONS
# ==============================================================================

# Common
t_en_info="INFO"
t_es_info="INFO"
t_en_error="ERROR"
t_es_error="ERROR"
t_en_success="SUCCESS"
t_es_success="ÉXITO"
t_en_warning="WARNING"
t_es_warning="AVISO"

# install.sh
t_en_checking_deps="Checking initial system dependencies..."
t_es_checking_deps="Comprobando dependencias iniciales del sistema..."
t_en_debug_mode="DEBUG MODE: Analysis and dry-run. No base packages will be manipulated."
t_es_debug_mode="MODO DEBUG: Análisis y dry-run. No se manipularán paquetes base."
t_en_installed="installed"
t_es_installed="instalado"
t_en_missing="missing"
t_es_missing="faltante"
t_en_installing_deps="Installing minimum required dependencies:"
t_es_installing_deps="Instalando dependencias mínimas requeridas:"
t_en_downloading_installer="Downloading main installer and components from GitHub..."
t_es_downloading_installer="Descargando instalador principal y componentes desde GitHub..."
t_en_download_success="Installer downloaded successfully."
t_es_download_success="Instalador descargado con éxito."
t_en_download_fallback="Could not download the installer from the internet. Using local fallback..."
t_es_download_fallback="No se pudo descargar el instalador de internet. Usando local fallback..."
t_en_fail_critical="Critical failure. Local installer not found."
t_es_fail_critical="Fallo crítico. Tampoco existe el instalador local."
t_en_fail_i18n="Critical failure. The localization module (i18n.py) is missing or empty."
t_es_fail_i18n="Fallo crítico. Falta el módulo de idiomas (i18n.py) o está vacío."
t_en_no_tty="No terminal available (/dev/tty). The installer may not be able to read your answers."
t_es_no_tty="No hay terminal disponible (/dev/tty). El instalador podría no poder leer tus respuestas."
t_en_launching_python="Launching Python installer..."
t_es_launching_python="Lanzando instalador Python..."

t_en_fail_installing_deps="Failed to install required dependencies. Please check your internet connection."
t_es_fail_installing_deps="Fallo al instalar las dependencias requeridas. Por favor, comprueba tu conexión a internet."

# refugios-ai-selector.sh
t_en_ai_selector_title="refugiOS - AI Model Selector"
t_es_ai_selector_title="refugiOS - Selector de Modelos de IA"
t_en_ai_no_models="No AI models installed.\n\nRun the refugiOS installer to download models first."
t_es_ai_no_models="No hay modelos de IA instalados.\n\nEjecuta el instalador de refugiOS para descargar modelos primero."
t_en_ai_hw_ram="RAM"
t_es_ai_hw_ram="RAM"
t_en_ai_hw_vram="VRAM"
t_es_ai_hw_vram="VRAM"
t_en_ai_hw_usable="Usable for AI"
t_es_ai_hw_usable="Utilizable para IA"
t_en_ai_hw_reserved="2GB OS reserved"
t_es_ai_hw_reserved="2GB reservados para el SO"
t_en_ai_select_model="Select an AI model to run:"
t_es_ai_select_model="Selecciona un modelo de IA para ejecutar:"
t_en_ai_err_resolve_model="Error: Could not resolve selected model."
t_es_ai_err_resolve_model="Error: No se pudo resolver el modelo seleccionado."
t_en_ai_llamafile_missing="The AI engine (llamafile) is not installed. Run the refugiOS installer and select the AI module."
t_es_ai_llamafile_missing="El motor de IA (llamafile) no está instalado. Ejecuta el instalador de refugiOS y selecciona el módulo de IA."
t_en_ai_waiting_server="Loading the model. This can take several minutes on slow drives, please wait..."
t_es_ai_waiting_server="Cargando el modelo. Puede tardar varios minutos en unidades lentas, espera por favor..."
t_en_ai_server_died="ERROR: the AI engine stopped while loading the model. Try a smaller model."
t_es_ai_server_died="ERROR: el motor de IA se ha detenido al cargar el modelo. Prueba con un modelo más pequeño."
t_en_ai_server_timeout="ERROR: the AI engine did not become ready in time. Try a smaller model."
t_es_ai_server_timeout="ERROR: el motor de IA no ha llegado a estar listo a tiempo. Prueba con un modelo más pequeño."
t_en_ai_purge_notice="Server Notice: Proceeding to purge the task. Please close this final black window to stop AI process consumption on your computer."
t_es_ai_purge_notice="Aviso de Servidor: Procediendo a purgar la tarea. Cierra por favor esta ventana negra final para erradicar el consumo del proceso IA de tu ordenador."

# refugios-maps.sh & refugios-kiwix.sh
t_en_maps_title="refugiOS - Maps"
t_es_maps_title="refugiOS - Mapas"
t_en_maps_not_installed="Organic Maps is not installed. Run the refugiOS installer to install it."
t_es_maps_not_installed="Organic Maps no está instalado. Ejecuta el instalador de refugiOS para instalarlo."
t_en_kiwix_not_found="Kiwix Desktop not found. Run the refugiOS installer to install it."
t_es_kiwix_not_found="Kiwix Desktop no encontrado. Ejecuta el instalador de refugiOS para instalarlo."
t_en_zim_not_found="ZIM file not found"
t_es_zim_not_found="Archivo ZIM no encontrado"

# refugios-vault scripts
t_en_vault_create="CREATING SECURE VAULT"
t_es_vault_create="CREANDO BÓVEDA SEGURA"
t_en_vault_open="OPENING SECURE VAULT"
t_es_vault_open="ABRIENDO BÓVEDA SEGURA"
t_en_vault_close="CLOSING SECURE VAULT"
t_es_vault_close="CERRANDO BÓVEDA SEGURA"
t_en_vault_password="Enter password for the vault:"
t_es_vault_password="Introduce la contraseña para la bóveda:"

# refugios-install-wrapper
t_en_wrapper_pinging="Checking Internet connection with github.com..."
t_es_wrapper_pinging="Comprobando conexión a Internet con github.com..."
t_en_wrapper_connected="Connection successful. Starting installer..."
t_es_wrapper_connected="Conexión exitosa. Iniciando instalador..."
t_en_no_connection_title="No Internet connection - refugiOS"
t_es_no_connection_title="Sin conexión a Internet - refugiOS"
t_en_no_connection_text="Could not connect to github.com.\n\nPlease connect to a WiFi or wired network before attempting the installation."
t_es_no_connection_text="No se pudo conectar con github.com.\n\nPor favor, conéctate a una red WiFi o cableada antes de intentar la instalación."
t_en_press_enter="Press ENTER to close..."
t_es_press_enter="Presiona ENTER para cerrar..."

# ==============================================================================
# FUNCTIONS
# ==============================================================================

# Get translation
t() {
    local key="$1"
    local lang="${REFUGIOS_LANG:-en}"
    local varname="t_${lang}_${key}"
    if [ -n "${!varname}" ]; then
        echo "${!varname}"
    else
        # Fallback to English
        varname="t_en_${key}"
        echo "${!varname:-$key}"
    fi
}

# Export the language, the lookup function and the strings it reads, so child
# processes get real translations instead of the raw key
export REFUGIOS_LANG
export -f t
for _refugios_str in ${!t_@}; do
    export "${_refugios_str?}"
done
unset _refugios_str
