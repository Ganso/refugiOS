#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
refugiOS - Instalador del Sistema (Python)
(Preparación del entorno y aplicaciones)

Descripción Extendida:
Este script se encarga de acondicionar el sistema operativo base para el uso de refugiOS.
Automatiza la descarga e instalación de herramientas base, paquetes en diferentes formatos 
(AppImage, Flatpak, APT), bases de conocimiento fuera de línea (Wikipedia, WikiMed, etc.),
descarga condicional de modelos de Inteligencia Artificial (LLMs) ejecutables en local, 
y la creación de entornos criptográficos seguros (Bóvedas).

El script requiere ejecución con permisos de usuario normal (NO root) y solicitará 
la contraseña para la elevación local vía `sudo` cuando necesite modificar el sistema.
"""

import os
import sys
import subprocess
import urllib.request
import json
import shutil
import re
import time

# ==============================================================================
# SECCIÓN 1: FUNCIONES DE UTILIDAD Y LOGS
# ==============================================================================

def log_info(msg):
    """Muestra un mensaje informativo en color azul."""
    print(f"\033[1;34m[*]\033[0m {msg}")

def log_err(msg):
    """Muestra un mensaje de error crítico en color rojo y finaliza la ejecución."""
    print(f"\033[1;31m[X] ERROR:\033[0m {msg}")
    sys.exit(1)

def log_success(msg):
    """Muestra un mensaje de éxito en color verde."""
    print(f"\033[1;32m[v] ÉXITO:\033[0m {msg}")

def run_cmd(cmd, shell=True, check=True, quiet=False):
    """
    Ejecuta un comando en la terminal del sistema.
    :param cmd: El comando a ejecutar (string).
    :param shell: Si es True, ejecuta a través de un shell (permite pipes, etc).
    :param check: Si es True, lanza excepción si el comando falla.
    :param quiet: Si es True, redirige la salida estándar y de errores a DEVNULL para un log más limpio.
    :return: True si el comando tuvo éxito, False en caso contrario.
    """
    try:
        stdout = subprocess.DEVNULL if quiet else None
        stderr = subprocess.DEVNULL if quiet else None
        subprocess.run(cmd, shell=shell, check=check, stdout=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"\033[1;33m[!] Aviso:\033[0m Comando falló al intentar ejecutar: {cmd}")
        return False
    return True

def get_cmd_output(cmd):
    """
    Ejecuta un comando en la terminal y retorna el texto (string) resultante de la salida estándar.
    Utilizado principalmente para obtener datos de consultas de información de hardware.
    """
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return result.stdout.strip()
    except Exception:
        return ""

# ==============================================================================
# SECCIÓN 2: DETECCIÓN Y DIAGNÓSTICO DEL SISTEMA
# ==============================================================================

class SystemInfo:
    """
    Clase que recaba, procesa y expone toda la información acerca de la computadora
    en la que se está ejecutando el script (SO, RAM, Almacenamiento, GPU).
    """
    def __init__(self):
        self.os_type = "Desconocido"
        self.is_rpi = False
        # Para saber si corre servidor gráfico antiguo (X11) o moderno (Wayland)
        self.desktop_env = os.environ.get("XDG_SESSION_TYPE", "Desconocido").capitalize()
        self.ram_mb = 0
        self.free_space_mb = 0
        self.gpu_info = "Desconocida"
        self.vram_info = "Desconocida"
        # Obtener idioma configurado en el sistema (ej: pasa de 'es_ES.UTF-8' a 'es')
        raw_lang = os.environ.get("LANG", "es").split('_')[0].lower()
        if raw_lang == "c" or len(raw_lang) != 2:
            self.lang = "es"
        else:
            self.lang = raw_lang
        
        self.detect_os()
        self.detect_ram()
        self.detect_storage()
        self.detect_gpu()

    def detect_os(self):
        """
        Determina si es Ubuntu, Debian o Raspberry Pi inspeccionando archivos nativos de Linux.
        """
        try:
            # Archivo genérico presente en la mayoría de distros Linux
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
            # Modelos físicos pregrabados (típico de placas de desarrollo ARM)
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model = f.read()
                if 'Raspberry Pi' in model:
                    self.is_rpi = True
                    self.os_type = "Raspberry Pi OS"
        except:
            pass

    def detect_ram(self):
        """Lee la cantidad de memoria RAM total instalada leyendo /proc/meminfo en formato KB y lo pasa a MB."""
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
        """Chequea el espacio disponible en disco en la partición donde está el sistema raíz (/)."""
        try:
            stat = shutil.disk_usage('/')
            self.free_space_mb = stat.free // (1024 * 1024)
        except:
            pass

    def detect_gpu(self):
        """
        Ejecuta llamadas al sistema (lspci) para determinar el tipo de tarjeta gráfica
        e intenta parsear su cantidad reservada de memoria VRAM (prefetchable memory segment).
        """
        out = get_cmd_output("lspci -v 2>/dev/null")
        if out:
            # Extraer el modelo exacto de la GPU
            vga_match = re.search(r'(VGA compatible controller|3D controller): (.*)', out)
            if vga_match:
                self.gpu_info = vga_match.group(2).strip()
                # Extraer la memoria "prefetchable" que comúnmente indica el volumen de memoria de video (VRAM)
                mem_match = re.search(r'Memory at .*?\(prefetchable\) \[size=([A-Za-z0-9]+)\]', out)
                if mem_match:
                    self.vram_info = mem_match.group(1)

# ==============================================================================
# SECCIÓN 3: MENÚS DE INTERACCIÓN MÚLTIPLE
# ==============================================================================

def multi_select_menu(title, options, default_indices=[]):
    """
    Muestra un menú con múltiples opciones que el usuario puede seleccionar al mismo tiempo
    al separar los índices por comas (ejemplo: '1,3' instalaría la opción 1 y la 3).
    
    :param title: Título decorativo del menú.
    :param options: Lista de diccionarios que definen las opciones disponibles, ej: [{'label': 'Opcion 1'}]
    :param default_indices: Lista de enteros con los índices pre-seleccionados por defecto.
    :return: Una lista de enteros correspondientes a los índices elegidos.
    """
    print(f"\n\033[1;36m=== {title} ===\033[0m")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt['label']}")
    print("  0) [No seleccionar nada / Saltar esta sección]")
    
    # Se añade +1 visualmente ya que los programadores cuentan desde 0, pero el usuario desde 1.
    if default_indices:
        default_str = ",".join(map(str, [i + 1 for i in default_indices]))
        prompt = f"Escribe los números separados por comas o 0 para omitir (Ej: 1,3) [Enter para recomendada: {default_str}]: "
    else:
        prompt = f"Escribe los números separados por comas o 0 para omitir [Enter para omitir]: "
    
    val = input(prompt).strip()
    if not val:
        # Retorna el valor sugerido si el usuario sólo pulsa Intro
        return default_indices
    
    selected = []
    for part in val.split(','):
        part = part.strip()
        if part == '0':
            return []
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(options):
                selected.append(idx)
    return selected

def single_select_menu(title, options, default_index):
    """
    Muestra un menú convencional en el que sólo es posible escoger un único número a la vez.
    """
    print(f"\n\033[1;36m=== {title} ===\033[0m")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt['label']}")
    print("  0) [No seleccionar nada / Saltar esta sección]")
    
    prompt = f"Opción [Enter para recomendada: {default_index + 1}]: "
    val = input(prompt).strip()
    if not val:
        return default_index
    if val == '0':
        return None
    if val.isdigit():
        idx = int(val) - 1
        if 0 <= idx < len(options):
            return idx
    return default_index

def simple_question(title, prompt_text, default_yes=False):
    """
    Muestra una cabecera de sección y realiza una pregunta interactiva de Sí/No.
    """
    print(f"\n\033[1;36m=== {title} ===\033[0m")
    if default_yes:
        val = input(f"{prompt_text} (S/n): ").strip().lower()
        return val != 'n'
    else:
        val = input(f"{prompt_text} (s/N): ").strip().lower()
        return val == 's'

# ==============================================================================
# SECCIÓN 4: GESTIÓN JERÁRQUICA DE PAQUETES
# ==============================================================================

class TargetEnv:
    """Mantiene mapeadas de forma centralizada todas las rutas (paths) críticas donde refugiOS guardará o leerá cosas."""
    def __init__(self, base_dir, desktop_dir):
        self.base = base_dir
        self.desktop = desktop_dir
        self.apps_dir = os.path.join(base_dir, "Apps", "versiones")
        self.know_dir = os.path.join(base_dir, "Conocimiento", "versiones")
        self.ia_dir = os.path.join(base_dir, "IA", "versiones")
        self.vault_dir = os.path.join(base_dir, "Bovedas")
        self.scripts_dir = os.path.join(base_dir, "Scripts")

def ensure_dirs(env):
    """Crea la estructura de carpetas maestras del proyecto sobre el disco duro si aún no existe."""
    log_info(f"Creando la estructura de directorios necesaria en {env.base}...")
    for d in [env.apps_dir, env.know_dir, env.ia_dir, env.vault_dir, env.scripts_dir]:
        os.makedirs(d, exist_ok=True)
    os.makedirs(env.desktop, exist_ok=True)

def install_package(env, name, is_rpi, appimage_url=None, appimage_name=None, flatpak_id=None, apt_deps=None):
    """
    El motor de despliegue principal. Intenta instalar el recurso siguiendo un comportamiento en cascada
    y prioridades, ideal para asegurar compatibilidad universal en distribuciones Linux convencionales.
    
    Jerarquía de intentos en Sistemas PC Normales:
       1) Intenta descargar como paquetizado portátil nativo de AppImage
       2) De fallar, intenta ubicarlo e instalarlo en el repositorio distribuido Flatpak
       3) En último caso, cae de vuelta a la API de paquetería madre APT (Debian/Ubuntu)
    
    Jerarquía en Sistemas ARM (Raspberry Pi):
       - Siempre interrumpe el ciclo e intenta forzar instalación mediante formato APT o interno
         dado que las AppImages prefabricadas a menudo carecen del binario ARM.
    """
    log_info(f"Instalando {name} mediante gestor jerárquico...")
    
    # Manejo Especial para Raspberry Pi:
    if is_rpi:
        if apt_deps:
            log_info(f"Modo Raspberry Pi: Bloqueando prioridades... Intentando instalación nativa APT de '{name}'...")
            if run_cmd(f"sudo apt-get install -y {apt_deps}", quiet=True):
                log_success(f"{name} se instaló nativamente vía APT.")
                return True
        log_info(f"No hay paquetes APT disponibles definidos para {name}. Se omitirá u empleará alternativa manual.")
        return False
        
    # PC - Nivel 1: Descarga AppImage
    if appimage_url and appimage_name:
        dest_path = os.path.join(env.apps_dir, appimage_name)
        if not os.path.exists(dest_path):
            log_info(f"Probando AppImage vía link directo: {appimage_name}")
            run_cmd(f"wget -c \"{appimage_url}\" -O \"{dest_path}\"")
        os.chmod(dest_path, 0o755)
        log_success(f"{name} resuelto e instalado vía AppImage.")
        return dest_path

    # PC - Nivel 2: Intento a través de Flatpak
    if flatpak_id:
        log_info(f"Saltando a repositorio Flatpak para resolver {name}...")
        # Nos aseguramos primero que Flathub esté presente en el equipo como repositorio activo.
        run_cmd("sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo", quiet=True)
        if run_cmd(f"sudo flatpak install flathub {flatpak_id} -y", quiet=True):
            log_success(f"{name} resuelto e instalado vía Flatpak.")
            return True
            
    # PC - Nivel 3: Retrocompatibilidad clásica mediante APT (Dependencias)
    if apt_deps:
        log_info(f"Sin resoluciones portables. Intentando {name} vía repositorio APT clásico...")
        if run_cmd(f"sudo apt-get install -y {apt_deps}", quiet=True):
            log_success(f"{name} resuelto e instalado recursivamente vía APT.")
            return True
            
    log_err(f"Agotados los 3 niveles de distribución. No fue posible instalar {name}.")
    return False

# ==============================================================================
# SECCIÓN 5: HERRAMIENTAS ADICIONALES (Web Scraping Básico)
# ==============================================================================

def fetch_url(url):
    """
    Realiza una solicitud HTTP simple y retorna el HTML/Texto de la respuesta simulando
    estar accediendo de incógnito con un User-Agent generalista de navegador web tradicional.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

# ==============================================================================
# BLOQUE MAESTRO: CONTROLADOR GENERAL (main)
# ==============================================================================
def main():
    # Salvaguarda de inicio para protección de permisos locales.
    if os.geteuid() == 0:
        log_err("Operación bloqueada. Este script instalador no debe ejecutarse como root. Ejecútalo como tu usuario habitual e introducirá 'sudo' sólo allá donde se necesite de manera interna.")

    # 1. Recuperación de Información Físico-Virtual.
    sys_info = SystemInfo()
    
    print("\n\033[1;36m=== DIAGNÓSTICO DEL SISTEMA ===\033[0m")
    print(f"Sistema Operativo: {sys_info.os_type}")
    print(f"Entorno de Escritorio: {sys_info.desktop_env}")
    print(f"Memoria RAM Detectada: {sys_info.ram_mb} MB")
    print(f"Capacidad Libre en Raíz: {sys_info.free_space_mb} MB")
    print(f"Hardware Gráfico: {sys_info.gpu_info}")
    print(f"VRAM / Memoria Video: {sys_info.vram_info}")
    print(f"Idioma Preferente: {sys_info.lang}")
    print("===============================\n")

    # Limitación formal si está en arquitectura de RPi con recursos débiles.
    if sys_info.is_rpi:
        print("\033[1;33m[!] ADVERTENCIA DE COMPATIBILIDAD:\033[0m")
        print("Se ha detectado arquitectura de placa Raspberry Pi. El soporte completo todavía se encuentra bajo investigación y se forzarán paquetes nativos de repositorios ARM.")
        ans = simple_question("IGNORAR ADVERTENCIA", "¿Deseas continuar a pesar de las limitaciones experimentales?", default_yes=False)
        if not ans:
            sys.exit(0)

    # El idioma es fundamental pues altera qué ficheros pesados se solicitan de los wikis (es, fr, en).
    print("En caso de que el perfil de idioma detectado automáticamente fuera incorrecto, corrígelo aquí (ejes: es, en, fr).")
    new_lang = input(f"Idioma por defecto [pulsa Intro para consolidar '{sys_info.lang}']: ").strip().lower()
    if new_lang: sys_info.lang = new_lang

    # Según el disco, ofrecemos versiones ligeras en texto o de alta calidad compuestas de imágenes (media rica).
    lite_mode = sys_info.free_space_mb < 25000
    if lite_mode:
        log_info("Se detectaron menos de 25 GB de almacenamiento. Se ha seleccionado la pre-configuración aligerada.")
        def_kb = [0] # Índice 0 = Solo Wikipedia Top Miniaturas
        def_ia = []  # Dejamos IA vacío por la restricción pesada
    else:
        log_info("Se detectaron recursos óptimos de almacenamiento. Se ha activado la pre-configuración enriquecida.")
        def_kb = [1] # Índice 1 = Wikipedia versión masificada completa (11 GB)
        def_ia = [0] # Índice 0 = Modelo conversacional base de Microsoft Phi-4

    # Criterio interno para cuando se abortan instalaciones a medias o se actualiza versiones viejas.
    force_dl = simple_question("MODO REESCRITURA", "¿Forzar descarga de componentes aunque ya existan?", default_yes=False)

    # ==========================
    # CUESTIONARIOS DEL INSTALADOR
    # ==========================

    # 1. Elección de Enciclopedias fuera de línea 
    kb_opts = [
        {"label": "Wikipedia versión Ligera [Artículos top, sin imágenes, resúmenes cortos] (~200 MB)", "type": "top_mini", "name": "wikipedia"},
        {"label": "Wikipedia Total Textual [Completa sin visuales grandes] (~11 GB)", "type": "all_nopic", "name": "wikipedia"},
        {"label": "WikiMed Enciclopedia de Salud Abierta (~1.5 GB)", "type": "maxi", "name": "wikimed"},
        {"label": "WikiHow Base de Conocimiento Práctico de Supervivencia y manualidades (~25-50 GB)", "type": "maxi", "name": "wikihow"}
    ]
    kb_selected = multi_select_menu("BASES DE DATOS DE CONOCIMIENTO (OFFLINE)", kb_opts, def_kb)

    # 2. Elección de Mapas (Opción de Organic Maps ahora puede omitirse según demanda del usuario)
    install_maps = simple_question("CARTOGRAFÍA (OFFLINE)", "¿Deseas instalar el módulo de Organic Maps para Cartografía y posicionamiento GPS Offline?", default_yes=True)

    # 2.5 Paquetes Extra: Ofimática y multimedia
    install_extras = simple_question("SOFTWARE OFIMÁTICO Y MULTIMEDIA", "¿Deseas instalar el paquete de software extra no directamente relacionado con la base (ofimática, reproducción de vídeos...)?", default_yes=True)

    # 3. Elección de Motores Inteligencia Artificial Auto-Hospedada (LLM)
    ia_opts = [
        {"label": "🟢 Mínimo: Emplear Microsoft Phi-4-mini (~2.5 GB almacenamiento | Requiere 4GB memoria RAM)"},
        {"label": "🟡 Intermedio: Emplear modelo analítico Qwen3-8B (~5 GB almacenamiento | Requiere 8GB memoria RAM)"},
        {"label": "🔴 Máximo: Emplear modelo complejo Qwen3-14B (~9 GB almacenamiento | Requiere 16GB memoria de cálculo)"}
    ]
    ia_selected = multi_select_menu("MODELOS DE INTELIGENCIA ARTIFICIAL (IA)", ia_opts, def_ia)

    # Configuración de red para P2P (Alivia servidores externos voluntarios usando Torrents)
    use_torrent = simple_question("RED PEER-TO-PEER (P2P)", "¿Priorizar descargas en P2P (BitTorrent) sobre descargas directas cuando sea posible?", default_yes=False)
    
    if not simple_question("CONFIRMACIÓN DE INSTALACIÓN", "Configuración terminada. ¿Deseas aplicar los cambios y comenzar la instalación ahora?", default_yes=False):
        log_err("La línea de comandos ha detenido formalmente la instalación.")

    if os.environ.get("DEBUG") == "1":
        print("\n\033[1;33m[!] MODO DEBUG:\033[0m Simulacro completado. Abandonando el proceso antes de realizar cambios estructurales o descargar ficheros.")
        sys.exit(0)

    # =========================================================
    # EJECUCIÓN E INSTALACIÓN FÍSICA
    # =========================================================

    # Definir dónde se posarán los lanzadores accesibles visualmente. Ubuntu Español vs Inglés.
    desktop_dir = os.path.join(os.environ['HOME'], "Escritorio")
    if not os.path.isdir(desktop_dir):
        desktop_dir = os.path.join(os.environ['HOME'], "Desktop")
    
    # Inicialización de Directorios Vitales
    base_dir = os.path.join(os.environ['HOME'], "refugiOS")
    env = TargetEnv(base_dir, desktop_dir)
    ensure_dirs(env)

    # Fase 1: Despliegue de Utilidades Internas del SO. (Bloque no AppImage, por lo que va directo al APT).
    log_info("Instalando el paquete de dependencias primario que nutre el resto del ecosistema...")
    
    base_pkgs = "curl wget aria2 jq rsync flatpak cryptsetup epiphany-browser gedit xfce4-terminal"
    if install_extras:
        log_info("Añadiendo suite multimedia y ofimática al instalador...")
        base_pkgs += " syncthing libreoffice vlc evince"
        
    run_cmd(f"sudo apt-get install -y {base_pkgs}", quiet=True)

    # Fase 2: Instalar la interfaz visual lectora Kiwix 
    # Esta interfaz decodifica la compresión .zim y te abre los wikis fuera de línea simulando Firefox.
    kiwix_appimage_url = None
    kiwix_appimage_name = None
    try:
        # Raspando su último código liberado del repositorio de descargas.
        html = fetch_url("https://download.kiwix.org/release/kiwix-desktop/")
        matches = re.findall(r'href="(kiwix-desktop_x86_64_[0-9.-]*\.appimage)"', html)
        if matches:
            # Una ordenación alfabética funciona aquí gracias a su nombrado de versión estricto.
            kiwix_appimage_name = sorted(matches)[-1]
            kiwix_appimage_url = f"https://download.kiwix.org/release/kiwix-desktop/{kiwix_appimage_name}"
    except Exception as e:
        print(f"\033[1;33m[!] Aviso:\033[0m Ruptura en decodificación buscando Kiwix AppImage base: {e}")

    # Envia a la máquina enrutadora que prioriza la versión obtenida.
    kiwix_path = install_package(env, "Lector de Enciclopedias (Kiwix Desktop)", sys_info.is_rpi, 
        appimage_url=kiwix_appimage_url, 
        appimage_name=kiwix_appimage_name, 
        flatpak_id="org.kiwix.desktop", 
        apt_deps="kiwix")

    # Creamos un atajo (Enlace simbólico) llamado sin versión, simplificando mantenimientos futuros.
    if isinstance(kiwix_path, str) and kiwix_path.endswith('.appimage'):
        run_cmd(f"ln -sf '{kiwix_path}' '{os.path.join(env.apps_dir, '../kiwix-desktop.appimage')}'")
        exec_path = os.path.join(env.base, "Apps", "kiwix-desktop.appimage")
    else:
        exec_path = "kiwix-desktop" if not sys_info.is_rpi else "kiwix"

    # Fase 3: Bases de Conocimiento (Peticiones complejas a granjas de datos de Kiwix Foundation)
    log_info("Analizando repositorios de conocimiento masivo ZIM...")
    for idx in kb_selected:
        opt = kb_opts[idx]
        log_info(f"Rastreando el archivo {opt['name']} correcto para enpaquetarlo en tu dispositivo...")
        zim_url = None
        zim_name = None
        html = ""
        base_search_url = ""
        # Wikihow reside en otro servidor (mirror exterior) debido a su extremo tamaño en algunos lenguajes.
        if opt['name'] == 'wikihow':
            base_search_url = "https://mirrors.dotsrc.org/kiwix/archive/zim/wikihow/"
        else:
            base_search_url = "https://download.kiwix.org/zim/wikipedia/"
        
        try:
            html = fetch_url(base_search_url)
            # Extracción del archivo ZIM con RegEx dinámico basado en las variables del entorno del usuario (ID, Idioma).
            # Ej: Genera `wikipedia_es_top_mini_2023-01.zim`
            if opt['name'] in ['wikipedia', 'wikimed']:
                regex = rf'href="(wikipedia_{sys_info.lang}_{opt["type"]}|{opt["type"]}_[A-Za-z0-9_-]*\.zim)"'
                if opt['name'] == 'wikimed':
                    regex = rf'href="(wikipedia_{sys_info.lang}_medicine_{opt["type"]}_[0-9-]*\.zim)"'
                elif opt['name'] == 'wikipedia':
                    regex = rf'href="(wikipedia_{sys_info.lang}_{opt["type"]}_[0-9-]*\.zim)"'
            elif opt['name'] == 'wikihow':
                regex = rf'href="(wikihow_{sys_info.lang}_{opt["type"]}_[0-9-]*\.zim)"'
            
            matches = re.findall(regex, html)
            if matches:
                 zim_name = sorted(matches)[-1]
                 zim_url = base_search_url + zim_name
        except:
             pass
        
        if zim_name and zim_url:
             target_zim = os.path.join(env.know_dir, zim_name)
             if os.path.exists(target_zim) and not force_dl:
                  log_info(f"El segmento {zim_name} ya figura localmente en el directorio de Conocimiento. No es necesaria interacción.")
             else:
                  log_info(f"Descargando archivo: {zim_name}...")
                  # Se usa Aria2 dado que sus conexiones múltiples asíncronas reducen críticamente los límites de red.
                  if use_torrent:
                       run_cmd(f"aria2c --seed-time=0 --continue=true --dir=\"{env.know_dir}\" \"{zim_url}.torrent\"")
                  else:
                       run_cmd(f"aria2c -x 4 --continue=true --auto-file-renaming=false --dir=\"{env.know_dir}\" -o \"{zim_name}\" \"{zim_url}\"")
             
             # Enlace para que el usuario o los scripts invoquen un archivo fijo pero enruten al cifrado descargado asumiendo su versión dinámica
             sym_name = f"{opt['name']}.zim"
             run_cmd(f"ln -sf '{target_zim}' '{os.path.join(env.base, 'Conocimiento', sym_name)}'")
             
             # Proveerle al usuario un lanzador gráfico decorativo directo a ese contenido específico en el escritorio.
             desktop_file = os.path.join(env.desktop, f"Conocimiento_{opt['name'].capitalize()}.desktop")
             with open(desktop_file, 'w') as f:
                  f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={opt['name'].capitalize()} (Offline Centralizado)
Comment=Acciona directamente el panel indexado y optimizado en caché de la base de registros en español.
Exec={exec_path} "{os.path.join(env.base, 'Conocimiento', sym_name)}"
Icon=accessories-dictionary
Terminal=false
""")
             os.chmod(desktop_file, 0o755)
        else:
             log_err(f"No fue posible encontrar el rastreador/descarga para el elemento ZIM subyacente a {opt['name']} sobre el idioma codificado {sys_info.lang}.")

    # Fase 4: Despliegue Cartográfico Opcional de Organic Maps OpenSource
    # Carga toda la cartografía en local a demanda sin depender de Google o cobertura celular.
    if install_maps:
        install_package(env, "Mapas GPS Offline (Organic Maps)", sys_info.is_rpi, flatpak_id="app.organicmaps.desktop")
        
        if sys_info.is_rpi:
            # Parche de bajo nivel si el entorno Pi sufre por el renderizado de OpenGL desde el contenedor.
            run_cmd("sudo flatpak override --device=dri app.organicmaps.desktop", quiet=True)
        
        with open(os.path.join(env.desktop, "Mapas_Offline.desktop"), "w") as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Mapas GPS (Organic Maps)
Exec=flatpak run app.organicmaps.desktop
Icon=app.organicmaps.desktop
Terminal=false
""")
        os.chmod(os.path.join(env.desktop, "Mapas_Offline.desktop"), 0o755)
    else:
        log_info("Se omitirá la provisión de las librerías cartográficas (Organic Maps).")

    # Función de ayuda para extraer los scripts externos de su repositorio principal
    repo_url = os.environ.get("REPO_URL", "https://raw.githubusercontent.com/Ganso/refugiOS/main")
    
    def fetch_script(s_name):
        d_path = os.path.join(env.scripts_dir, s_name)
        ok = run_cmd(f"wget -q -c \"{repo_url}/scripts/{s_name}\" -O \"{d_path}\"", quiet=True)
        if not ok or not os.path.exists(d_path) or os.path.getsize(d_path) == 0:
            local_dir = os.path.dirname(os.path.realpath(__file__))
            local_s = os.path.join(local_dir, "scripts", s_name)
            if os.path.exists(local_s):
                shutil.copy(local_s, d_path)
            else:
                log_err(f"No fue posible ubicar el {s_name} remoto ni local.")
        os.chmod(d_path, 0o755)
        return d_path

    # Fase 5: IA Residente e Inferencia de Lenguaje Natural (Llamafile portado para ser autónomo).
    if ia_selected:
        log_info("Estableciendo fundaciones del motor central cognitivo, Llamafile...")
        try:
             # Exploración a través de las APIs públicas de las empresas de desarrollo para su ejecutador final.
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
                  l_path = os.path.join(env.ia_dir, llama_name)
                  if not os.path.exists(l_path) or force_dl:
                       run_cmd(f"wget -c \"{llama_url}\" -O \"{l_path}\"")
                  os.chmod(l_path, 0o755)
                  
                  # Asignar un hiperenlace permanente en el directorio
                  run_cmd(f"ln -sf '{l_path}' '{os.path.join(env.base, 'IA', 'llamafile')}'")
        except:
             log_err("Error al conectar con GitHub para obtener Llamafile.")

        # Los vectores pre-entrenados del modelo GGUF basados puramente en su escala.
        modelos = [
            ("microsoft_Phi-4-mini-instruct-Q4_K_M.gguf", "https://huggingface.co/bartowski/microsoft_Phi-4-mini-instruct-GGUF/resolve/main/", "modelo-basico.gguf"),
            ("Qwen_Qwen3-8B-Q4_K_M.gguf", "https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF/resolve/main/", "modelo-medio.gguf"),
            ("Qwen_Qwen3-14B-Q4_K_M.gguf", "https://huggingface.co/bartowski/Qwen_Qwen3-14B-GGUF/resolve/main/", "modelo-avanzado.gguf")
        ]
        
        for idx in ia_selected:
            filename, url_base, symlink = modelos[idx]
            full_url = url_base + filename
            m_path = os.path.join(env.ia_dir, filename)
            if not os.path.exists(m_path) or force_dl:
                 log_info(f"Descargando archivo: {filename}...")
                 run_cmd(f"wget -c \"{full_url}\" -O \"{m_path}\"")
            run_cmd(f"ln -sf '{m_path}' '{os.path.join(env.base, 'IA', symlink)}'")

        script_path = fetch_script("refugios-ia-selector.sh")
        
        with open(os.path.join(env.desktop, "Asistente_IA.desktop"), "w") as f:
             f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Asistente IA Local
Exec=xfce4-terminal -e "{script_path}"
Icon=utilities-terminal
Terminal=false
""")
        os.chmod(os.path.join(env.desktop, "Asistente_IA.desktop"), 0o755)

    # Fase 6: Cimientos Criptográficos de Privacidad
    log_info("Ensamblando bóvedas de seguridad y directivas de privacidad...")
    
    v_create = fetch_script("refugios-vault-create.sh")
    v_open = fetch_script("refugios-vault-open.sh")
    v_close = fetch_script("refugios-vault-close.sh")

    # Interfaz gráfica sobre los módulos criptográficos.
    for i, name, script, icon in [
        (1, "Crear nueva Bóveda Segura (Solo la primera vez)", v_create, "dialog-password"),
        (2, "Abrir Bóveda Segura", v_open, "folder-open"),
        (3, "Cerrar y Sellar Bóveda Activa", v_close, "system-lock-screen")
    ]:
        dfile = os.path.join(env.desktop, f"{i}_{name.replace(' ', '_')}.desktop")
        with open(dfile, "w") as f:
            f.write(f"""[Desktop Entry]
Type=Application
Name={i}. {name}
Exec=xfce4-terminal -e "{script}"
Icon={icon}
Terminal=false
""")
        os.chmod(dfile, 0o755)

    # Eliminación de alertas para los gestores modulares del software sobre ejecutables carentes de firma formal.
    log_info("Certificando atajos y deshabilitando avisos de seguridad del escritorio local...")
    if shutil.which("gio"):
        for file in os.listdir(env.desktop):
            if file.endswith('.desktop'):
                fpath = os.path.join(env.desktop, file)
                run_cmd(f"gio set '{fpath}' metadata::trusted yes", quiet=True)
                # Parche para XFCE de Checksum
                checksum = get_cmd_output(f"sha256sum '{fpath}' | awk '{{print $1}}'")
                if checksum:
                    run_cmd(f"gio set '{fpath}' metadata::xfce-exe-checksum '{checksum}'", quiet=True)

    # Parche para LXDE / PCManFM (Típico en Raspberry Pi)
    libfm_conf = os.path.join(os.environ['HOME'], ".config", "libfm", "libfm.conf")
    if os.path.exists(libfm_conf):
        run_cmd(f"sed -i 's/quick_exec=0/quick_exec=1/' '{libfm_conf}'", quiet=True)
        if not 'quick_exec=1' in open(libfm_conf).read():
            run_cmd(f"echo -e '\n[General]\nquick_exec=1' >> '{libfm_conf}'", quiet=True)

    log_success("LA OPERACIÓN GLOBAL DE DESPLIEGUE FINALIZÓ. Revisa la integridad y accesibilidad de los iconos en el área de tu escritorio.")


# Puerta de entrada estricta al intérprete evitando que se llame importando como módulo.
if __name__ == "__main__":
    main()
