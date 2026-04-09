#!/bin/bash
# refugiOS - Localization System (Bash)

# Default language
REFUGIOS_LANG="en"

# Load persistent language from config file
LANG_CONFIG="$HOME/.refugios_lang"
if [ -f "$LANG_CONFIG" ]; then
    REFUGIOS_LANG=$(cat "$LANG_CONFIG")
fi

# Override with environment variable if present (useful for autodetection before persistence)
if [ -n "$LANG" ]; then
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
t_en_launching_python="Launching Python installer..."
t_es_launching_python="Lanzando instalador Python..."

# refugios-ai-selector.sh
t_en_ai_purge_notice="Server Notice: Proceeding to purge the task. Please close this final black window to stop AI process consumption on your computer."
t_es_ai_purge_notice="Aviso de Servidor: Procediendo a purgar la tarea. Cierra por favor esta ventana negra final para erradicar el consumo del proceso IA de tu ordenador."

# refugios-vault scripts
t_en_vault_create="CREATING SECURE VAULT"
t_es_vault_create="CREANDO BÓVEDA SEGURA"
t_en_vault_open="OPENING SECURE VAULT"
t_es_vault_open="ABRIENDO BÓVEDA SEGURA"
t_en_vault_close="CLOSING SECURE VAULT"
t_es_vault_close="CERRANDO BÓVEDA SEGURA"
t_en_vault_password="Enter password for the vault:"
t_es_vault_password="Introduce la contraseña para la bóveda:"

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

# Export the language for child processes
export REFUGIOS_LANG
