import os

# Default language
REFUGIOS_LANG = "en"

# Config file path
LANG_CONFIG = os.path.expanduser("~/.refugios_lang")

def load_lang():
    global REFUGIOS_LANG
    if os.path.exists(LANG_CONFIG):
        try:
            with open(LANG_CONFIG, 'r') as f:
                lang = f.read().strip()
                if lang in ["es", "en"]:
                    REFUGIOS_LANG = lang
        except:
            pass
    else:
        # Autodetect from environment
        raw_lang = os.environ.get("LANG", "").split('_')[0].lower()
        if raw_lang in ["es", "en"]:
            REFUGIOS_LANG = raw_lang

def save_lang(lang):
    global REFUGIOS_LANG
    if lang in ["es", "en"]:
        REFUGIOS_LANG = lang
        try:
            with open(LANG_CONFIG, 'w') as f:
                f.write(lang)
            
            # Update .bashrc for persistence across sessions
            bashrc = os.path.expanduser("~/.bashrc")
            export_line = f'export LANG={lang}_{"US" if lang == "en" else "ES"}.UTF-8'
            
            content = ""
            if os.path.exists(bashrc):
                with open(bashrc, 'r') as f:
                    content = f.read()
            
            lines = content.splitlines()
            new_lines = [l for l in lines if not l.startswith("export LANG=")]
            new_lines.append(export_line)
            
            with open(bashrc, 'w') as f:
                f.write("\n".join(new_lines) + "\n")
        except:
            pass

TRANSLATIONS = {
    'en': {
        'info': 'INFO',
        'error': 'ERROR',
        'success': 'SUCCESS',
        'warning': 'WARNING',
        'yes': 'Yes',
        'no': 'No',
        'installed_tag': '[installed]',
        'sys_diag_title': 'System Diagnosis - refugiOS',
        'os_label': 'OPERATING SYSTEM',
        'rpi_model_label': 'RASPBERRY PI MODEL',
        'desktop_env_label': 'DESKTOP ENVIRONMENT',
        'ram_label': 'RAM MEMORY',
        'disk_space_label': 'DISK SPACE',
        'gpu_label': 'GRAPHICS HARDWARE',
        'vram_label': 'DETECTED VRAM',
        'detected_lang_label': 'DETECTED LANGUAGE',
        'rpi_arch_detected': 'RASPBERRY PI ARCHITECTURE DETECTED.\nNATIVE ARM PACKETS WILL BE USED.',
        'detect_lang_prompt': 'Detect system language.\nIf it is incorrect, correct it here (examples: es, en):',
        'lang_config_title': 'Language Configuration',
        'lite_mode_msg': 'Less than 25 GB of storage detected. Lightweight pre-configuration selected.',
        'rich_mode_msg': 'Optimal storage resources detected. Enriched pre-configuration activated.',
        'rewrite_mode_title': 'REWRITE MODE',
        'rewrite_mode_prompt': 'Do you want to force the download of components even if they already exist locally?',
        'kb_menu_title': 'KNOWLEDGE DATABASES (OFFLINE)',
        'maps_menu_title': 'CARTOGRAPHY (OFFLINE)',
        'maps_menu_prompt': 'Do you want to install the Organic Maps module for Offline Cartography and GPS positioning?',
        'extras_menu_title': 'OFFICE AND MULTIMEDIA SOFTWARE',
        'extras_menu_prompt': 'Do you want to install the extra software package (LibreOffice, VLC, etc.)?',
        'ia_menu_title': 'ARTIFICIAL INTELLIGENCE MODELS (AI)',
        'p2p_menu_title': 'PEER-TO-PEER NETWORK (P2P)',
        'p2p_menu_prompt': 'Prioritize P2P (BitTorrent) downloads over direct downloads?',
        'confirm_install_title': 'INSTALLATION CONFIRMATION',
        'confirm_install_prompt': 'Configuration finished. Do you want to apply changes and start installation now?',
        'install_aborted': 'The command line has formally stopped the installation.',
        'debug_simulation': 'DEBUG MODE: Simulation completed. Abandoning process before structural changes or downloads.',
        'creating_dirs': 'Creating the necessary directory structure in {0}...',
        'syncing_resources': 'Synchronizing links and launchers with resources on disk...',
        'obsolete_icon': 'Obsolete icon removed: {0}',
        'fixing_perms': 'Preparing package manager and resolving possible blocks...',
        'installing_base_deps': 'Installing primary dependency package that fuels the rest of the ecosystem...',
        'adding_extras': 'Adding multimedia and office suite to the installer...',
        'syncing_lang_pkgs': "Synchronizing language packages for '{0}'...",
        'optimizing_pcmanfm': 'Optimizing PCManFM configuration for script execution...',
        'patching_apparmor': 'AppArmor restriction detected on namespaces. Applying system patch...',
        'installing_package': 'Installing {0} via hierarchical manager...',
        'installed_apt': '{0} was installed natively via APT.',
        'installed_appimage': '{0} resolved and installed via AppImage.',
        'installed_flatpak': '{0} resolved and installed via Flatpak.',
        'installed_recursive_apt': '{0} resolved and installed recursively via APT.',
        'install_failed': 'Exhausted 3 distribution levels. It was not possible to install {0}.',
        'scanning_zim': 'Analyzing ZIM massive knowledge repositories...',
        'tracking_zim': "Tracking the correct {0} ({1}) file...",
        'zim_exists': "Segment {0} is already local. No interaction needed.",
        'downloading_zim': "Downloading file: {0}...",
        'zim_not_found': "Could not find tracker for {0} ({1}) in {2}.",
        'fetching_scripts': "Fetching internal scripts...",
        'script_not_found': "Could not locate remote or local {0}.",
        'maps_gps_name': "GPS Maps",
        'wikipedia_comment': "Free offline encyclopedia.",
        'generic_zim_comment': "Offline resource available without connection.",
        'dialog_error': "Error: 'python3-dialog' library not found.\nMake sure to run 'install.sh' first or install the package manually.",
        'wiki_lite_label': "Wikipedia Lightweight [Top articles, no images, short summaries] (~200 MB)",
        'wiki_total_label': "Wikipedia Total Textual [Complete without large visuals] (~11 GB)",
        'wikimed_label': "WikiMed Open Health Encyclopedia (~1.5 GB)",
        'wikihow_label': "WikiHow Practical Knowledge Base (~25-50 GB)",
        'ia_min_label': "Minimum: Use Qwen2.5-0.5B (~0.5 GB storage | Requires 1GB RAM)",
        'ia_base_label': "Basic: Use Microsoft Phi-4-mini (~2.5 GB storage | Requires 4GB RAM)",
        'ia_med_label': "Intermediate: Use Qwen3-8B analytical model (~5 GB storage | Requires 8GB RAM)",
        'ia_max_label': "Maximum: Use Qwen3-14B complex model (~9 GB storage | Requires 16GB RAM)"
    },
    'es': {
        'info': 'INFO',
        # ...
        'error': 'ERROR',
        'success': 'ÉXITO',
        'warning': 'AVISO',
        'yes': 'Sí',
        'no': 'No',
        'installed_tag': '[instalado]',
        'sys_diag_title': 'Diagnóstico de Sistema - refugiOS',
        'os_label': 'SISTEMA OPERATIVO',
        'rpi_model_label': 'MODELO RASPBERRY PI',
        'desktop_env_label': 'ENTORNO DE ESCRITORIO',
        'ram_label': 'MEMORIA RAM',
        'disk_space_label': 'ESPACIO DISCO',
        'gpu_label': 'HARDWARE GRÁFICO',
        'vram_label': 'VRAM DETECTADA',
        'detected_lang_label': 'IDIOMA DETECTADO',
        'rpi_arch_detected': 'ARQUITECTURA RASPBERRY PI DETECTADA.\nSE USARÁN PAQUETES NATIVOS ARM.',
        'detect_lang_prompt': 'Detectar idioma del sistema.\nEn caso de que fuera incorrecto, corrígelo aquí (ejemplos: es, en):',
        'lang_config_title': 'Configuración de Idioma',
        'lite_mode_msg': 'Se detectaron menos de 25 GB de almacenamiento. Se ha seleccionado la pre-configuración aligerada.',
        'rich_mode_msg': 'Se detectaron recursos óptimos de almacenamiento. Se ha activado la pre-configuración enriquecida.',
        'rewrite_mode_title': 'MODO REESCRITURA',
        'rewrite_mode_prompt': '¿Deseas forzar la descarga de componentes aunque ya existan localmente?',
        'kb_menu_title': 'BASES DE DATOS DE CONOCIMIENTO (OFFLINE)',
        'maps_menu_title': 'CARTOGRAFÍA (OFFLINE)',
        'maps_menu_prompt': '¿Deseas instalar el módulo de Organic Maps para Cartografía y posicionamiento GPS Offline?',
        'extras_menu_title': 'SOFTWARE OFIMÁTICO Y MULTIMEDIA',
        'extras_menu_prompt': '¿Deseas instalar el paquete de software extra (LibreOffice, VLC, etc.)?',
        'ia_menu_title': 'MODELOS DE INTELIGENCIA ARTIFICIAL (IA)',
        'p2p_menu_title': 'RED PEER-TO-PEER (P2P)',
        'p2p_menu_prompt': '¿Priorizar descargas en P2P (BitTorrent) sobre descargas directas?',
        'confirm_install_title': 'CONFIRMACIÓN DE INSTALACIÓN',
        'confirm_install_prompt': 'Configuración terminada. ¿Deseas aplicar los cambios y comenzar la instalación ahora?',
        'install_aborted': 'La línea de comandos ha detenido formalmente la instalación.',
        'debug_simulation': 'MODO DEBUG: Simulacro completado. Abandonando el proceso antes de realizar cambios estructurales o descargar ficheros.',
        'creating_dirs': 'Creando la estructura de directorios necesaria en {0}...',
        'syncing_resources': 'Sincronizando enlaces y lanzadores con los recursos en disco...',
        'obsolete_icon': 'Icono obsoleto eliminado: {0}',
        'fixing_perms': 'Preparando gestor de paquetes y resolviendo posibles bloqueos...',
        'installing_base_deps': 'Instalando el paquete de dependencias primario que nutre el resto del ecosistema...',
        'adding_extras': 'Añadiendo suite multimedia y ofimática al instalador...',
        'syncing_lang_pkgs': "Sincronizando paquetes de idioma para '{0}'...",
        'optimizing_pcmanfm': 'Optimizando configuración de PCManFM para ejecución de scripts...',
        'patching_apparmor': 'Detectada restricción de AppArmor sobre namespaces. Aplicando parche de sistema...',
        'installing_package': 'Instalando {0} mediante gestor jerárquico...',
        'installed_apt': '{0} se instaló nativamente vía APT.',
        'installed_appimage': '{0} resuelto e instalado vía AppImage.',
        'installed_flatpak': '{0} resuelto e instalado vía Flatpak.',
        'installed_recursive_apt': '{0} resuelto e instalado recursivamente vía APT.',
        'install_failed': 'Agotados los 3 niveles de distribución. No fue posible instalar {0}.',
        'scanning_zim': 'Analizando repositorios de conocimiento masivo ZIM...',
        'tracking_zim': "Rastreando el archivo {0} ({1}) correcto...",
        'zim_exists': "El segmento {0} ya figura localmente. No es necesaria interacción.",
        'downloading_zim': "Descargando archivo: {0}...",
        'zim_not_found': "No fue posible encontrar el rastreador para {0} ({1}) en {2}.",
        'fetching_scripts': "Descargando scripts internos...",
        'script_not_found': "No fue posible ubicar el {0} remoto ni local.",
        'maps_gps_name': "Mapas GPS",
        'wikipedia_comment': "Enciclopedia libre offline.",
        'generic_zim_comment': "Recurso offline disponible sin conexión.",
        'dialog_error': "ERROR: No se encontró la librería 'python3-dialog'.\nAsegúrate de ejecutar 'install.sh' primero o instala el paquete manualmente.",
        'wiki_lite_label': "Wikipedia versión Ligera [Artículos top, sin imágenes, resúmenes cortos] (~200 MB)",
        'wiki_total_label': "Wikipedia Total Textual [Completa sin visuales grandes] (~11 GB)",
        'wikimed_label': "WikiMed Enciclopedia de Salud Abierta (~1.5 GB)",
        'wikihow_label': "WikiHow Base de Conocimiento Práctico (~25-50 GB)",
        'ia_min_label': "Mínimo: Emplear Qwen2.5-0.5B (~0.5 GB almacenamiento | Requiere 1GB RAM)",
        'ia_base_label': "Básico: Emplear Microsoft Phi-4-mini (~2.5 GB almacenamiento | Requiere 4GB RAM)",
        'ia_med_label': "Intermedio: Emplear modelo analítico Qwen3-8B (~5 GB almacenamiento | Requiere 8GB RAM)",
        'ia_max_label': "Máximo: Emplear modelo complejo Qwen3-14B (~9 GB almacenamiento | Requiere 16GB RAM)"
    }
}

def T(key):
    lang_dict = TRANSLATIONS.get(REFUGIOS_LANG, TRANSLATIONS['en'])
    # Return translated string, or fallback to English, or key itself if everything fails
    return lang_dict.get(key, TRANSLATIONS['en'].get(key, key))

load_lang()
