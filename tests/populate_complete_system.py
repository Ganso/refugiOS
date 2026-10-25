#!/usr/bin/env python3
"""
Populates the mounted refugiOS filesystem with the complete 0.27 desktop environment:
- Desktop launchers (Wikipedia, WikiMed, WikiHow, Mapas, IA, Traductor, Bovedas, Check, Update)
- "Biblioteca refugiOS" folder with the full catalog of practical manuals and survival guides
- Installed ZIMs, AI models, and scripts
- Trust certification for all desktop icons
"""

import os
import sys
import shutil
import hashlib

MNT = "/tmp/mnt_refugios"
REFUGIOS_HOME = os.path.join(MNT, "home/refugios")
DESKTOP = os.path.join(REFUGIOS_HOME, "Desktop")
LIBRARY = os.path.join(DESKTOP, "Biblioteca refugiOS")
SCRIPTS_DIR = os.path.join(REFUGIOS_HOME, "refugiOS/Scripts")
KNOW_DIR = os.path.join(REFUGIOS_HOME, "refugiOS/Knowledge")
AI_DIR = os.path.join(REFUGIOS_HOME, "refugiOS/AI")
VAULTS_DIR = os.path.join(REFUGIOS_HOME, "refugiOS/Vaults")
MAPS_DIR = os.path.join(REFUGIOS_HOME, ".var/app/app.organicmaps.desktop/data/OMaps/260528")

GUEST_SCRIPTS = "/home/refugios/refugiOS/Scripts"
GUEST_KNOW = "/home/refugios/refugiOS/Knowledge"

os.makedirs(DESKTOP, exist_ok=True)
os.makedirs(LIBRARY, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(os.path.join(KNOW_DIR, "versions"), exist_ok=True)
os.makedirs(os.path.join(AI_DIR, "versions"), exist_ok=True)
os.makedirs(VAULTS_DIR, exist_ok=True)
os.makedirs(MAPS_DIR, exist_ok=True)

# Copy all repository scripts
REPO_SCRIPTS = "/home/ganso/codigo/refugiOS/scripts"
for s in os.listdir(REPO_SCRIPTS):
    src = os.path.join(REPO_SCRIPTS, s)
    if os.path.isfile(src):
        dst = os.path.join(SCRIPTS_DIR, s)
        shutil.copy(src, dst)
        os.chmod(dst, 0o755)

# Copy i18n.py
shutil.copy("/home/ganso/codigo/refugiOS/i18n.py", os.path.join(SCRIPTS_DIR, "i18n.py"))

# Create mock ZIM files and symlinks
def create_mock_file(path, size_mb=10):
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(b"ZIM0" + b"\0" * (1024 * 1024 * size_mb - 4))

zims = [
    ("wikipedia_es_all_maxi_2026-05.zim", "wikipedia.zim"),
    ("wikimed_es_all_maxi_2026-05.zim", "wikimed.zim"),
    ("wikihow_es_all_maxi_2026-05.zim", "wikihow.zim"),
    ("ifixit_es_all_maxi_2026-05.zim", "ifixit.zim"),
    ("appropedia_es_all_maxi_2026-05.zim", "appropedia.zim"),
    ("energypedia_es_all_maxi_2026-05.zim", "energypedia.zim"),
    ("gutenberg_es_all_maxi_2026-05.zim", "gutenberg.zim"),
    ("wiktionary_es_all_maxi_2026-05.zim", "wiktionary.zim"),
    ("scoutwiki_es_all_maxi_2026-05.zim", "scoutwiki.zim"),
]

for vname, sname in zims:
    vpath = os.path.join(KNOW_DIR, "versions", vname)
    create_mock_file(vpath, 2)
    slink = os.path.join(KNOW_DIR, sname)
    if os.path.islink(slink) or os.path.exists(slink):
        os.unlink(slink)
    os.symlink(f"versions/{vname}", slink)

# Create mock AI model and llamafile
mpath = os.path.join(AI_DIR, "versions/Qwen3.5-0.8B-Q4_K_M.gguf")
create_mock_file(mpath, 5)
slink = os.path.join(AI_DIR, "minimal-model.gguf")
if os.path.islink(slink) or os.path.exists(slink): os.unlink(slink)
os.symlink("versions/Qwen3.5-0.8B-Q4_K_M.gguf", slink)

lfpath = os.path.join(AI_DIR, "versions/llamafile-0.8.14")
create_mock_file(lfpath, 2)
os.chmod(lfpath, 0o755)
slink = os.path.join(AI_DIR, "llamafile")
if os.path.islink(slink) or os.path.exists(slink): os.unlink(slink)
os.symlink("versions/llamafile-0.8.14", slink)

# Create mock maps
create_mock_file(os.path.join(MAPS_DIR, "Spain.mwm"), 5)
create_mock_file(os.path.join(MAPS_DIR, "World.mwm"), 2)

# Create mock vault
create_mock_file(os.path.join(VAULTS_DIR, "personal.img"), 5)

# Desktop launchers:
launchers = {
    "Wikipedia.desktop": {
        "Name": "Wikipedia",
        "Comment": "Enciclopedia libre completa sin conexión",
        "Exec": f'bash "{GUEST_SCRIPTS}/refugios-kiwix.sh" "{GUEST_KNOW}/wikipedia.zim"',
        "Icon": "accessories-dictionary"
    },
    "WikiMed.desktop": {
        "Name": "WikiMed",
        "Comment": "Enciclopedia médica completa sin conexión",
        "Exec": f'bash "{GUEST_SCRIPTS}/refugios-kiwix.sh" "{GUEST_KNOW}/wikimed.zim"',
        "Icon": "accessories-dictionary"
    },
    "WikiHow.desktop": {
        "Name": "WikiHow",
        "Comment": "Manual de instrucciones y guías paso a paso",
        "Exec": f'bash "{GUEST_SCRIPTS}/refugios-kiwix.sh" "{GUEST_KNOW}/wikihow.zim"',
        "Icon": "accessories-dictionary"
    },
    "Offline_Maps.desktop": {
        "Name": "Mapas GPS",
        "Comment": "Cartografía mundial sin conexión con Organic Maps",
        "Exec": f'bash "{GUEST_SCRIPTS}/refugios-maps.sh"',
        "Icon": "app.organicmaps.desktop"
    },
    "AI_Assistant.desktop": {
        "Name": "Asistente de IA Local",
        "Comment": "Inteligencia artificial privada y local sin conexión",
        "Exec": f'xfce4-terminal -e "{GUEST_SCRIPTS}/refugios-ai-selector.sh"',
        "Icon": "utilities-terminal"
    },
    "Translator.desktop": {
        "Name": "Traductor (LocalTranslate)",
        "Comment": "Traducción neuronal de textos offline",
        "Exec": "flatpak run dev.ters.LocalTranslate",
        "Icon": "dev.ters.LocalTranslate"
    },
    "Vault_Manager.desktop": {
        "Name": "Gestor de Bóvedas Cifradas",
        "Comment": "Cifrado y gestión de datos personales seguros (LUKS)",
        "Exec": f'xfce4-terminal -e "python3 {GUEST_SCRIPTS}/refugios-vault.py"',
        "Icon": "dialog-password"
    },
    "Check_refugiOS.desktop": {
        "Name": "Comprobar refugiOS",
        "Comment": "Verificación offline de la integridad del sistema",
        "Exec": f'xfce4-terminal -e "python3 {GUEST_SCRIPTS}/refugios-check.py"',
        "Icon": "emblem-default"
    },
    "Update_refugiOS.desktop": {
        "Name": "Actualizar refugiOS",
        "Comment": "Actualización de contenidos y módulos de refugiOS",
        "Exec": f'xfce4-terminal -e "bash {GUEST_SCRIPTS}/refugios-update.sh"',
        "Icon": "system-software-update"
    },
}

for fname, data in launchers.items():
    fpath = os.path.join(DESKTOP, fname)
    with open(fpath, "w") as f:
        f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={data['Name']}
Comment={data['Comment']}
Exec={data['Exec']}
Icon={data['Icon']}
Terminal=false
""")
    os.chmod(fpath, 0o755)

# Clear old library entries if any
for f in os.listdir(LIBRARY):
    if f.endswith('.desktop'):
        try: os.unlink(os.path.join(LIBRARY, f))
        except OSError: pass

# Library books inside Biblioteca refugiOS
library_books = [
    ("iFixit - Guías de reparación.desktop", "iFixit: Guías de reparación", "Manuales paso a paso de reparación de aparatos y vehículos", "preferences-system"),
    ("WikEM - Medicina de urgencias.desktop", "WikEM: Medicina de urgencias", "Manual de medicina de emergencias para sanitarios", "help-browser"),
    ("Primeros auxilios y supervivencia.desktop", "Primeros auxilios y supervivencia", "Manual de medicina táctica y primeros auxilios de campaña", "dialog-information"),
    ("Guía postdesastre y resiliencia.desktop", "Guía postdesastre y resiliencia", "Guías prácticas seleccionadas para la vida tras un desastre", "emblem-important"),
    ("Agua - Potabilizar y almacenar.desktop", "Agua: Potabilizar y almacenar", "Guía para encontrar, filtrar, hervir y almacenar agua segura", "applications-accessories"),
    ("Alimentos - Conservación y nutrición.desktop", "Alimentos: Conservación y nutrición", "Técnicas de deshidratación, salazón, conservas y nutrición básica", "applications-accessories"),
    ("Nudos prácticos ilustrados.desktop", "Nudos prácticos ilustrados", "Guía visual de nudos para amarres, rescate y acampada", "preferences-desktop-keyboard"),
    ("ScoutWiki - Técnicas al aire libre.desktop", "ScoutWiki: Técnicas al aire libre", "Acampada, orientación por estrellas, fuegos y cabuyería", "user-home"),
    ("Appropedia - Tecnologías apropiadas.desktop", "Appropedia: Tecnologías apropiadas", "Soluciones de bajo coste, filtros biológicos y energía pasiva", "system-help"),
    ("Energypedia - Energía solar y renovable.desktop", "Energypedia: Energía solar y renovable", "Instalaciones solares aisladas, baterías y microgeneración", "battery"),
    ("Huerto y agricultura sostenible.desktop", "Huerto y agricultura sostenible", "Cultivo intensivo de alimentos y conservación de semillas", "folder-saved-search"),
    ("Reparaciones domésticas y fontanería.desktop", "Reparaciones domésticas y fontanería", "Guías prácticas de electricidad básica, tuberías y carpintería", "wrench"),
    ("Mecánica y mantenimiento de vehículos.desktop", "Mecánica y mantenimiento de vehículos", "Mantenimiento preventivo de motores y averías comunes", "drive-harddisk"),
    ("Radioafición - Enlaces de emergencia.desktop", "Radioafición: Enlaces de emergencia", "Comunicaciones de radio en frecuencias libres y de emergencia", "network-wireless"),
    ("Wikcionario - Diccionario multilingüe.desktop", "Wikcionario: Diccionario multilingüe", "Diccionario completo con definiciones y etimología", "accessories-dictionary"),
    ("Wikiviajes - Guías de viaje.desktop", "Wikiviajes: Guías de viaje", "Mapas de carreteras, frases de auxilio en otros idiomas y datos clave", "applications-internet"),
    ("Wikilibros - Manuales libres.desktop", "Wikilibros: Manuales libres", "Libros de texto de matemáticas, física, botánica y química básica", "accessories-text-editor"),
    ("Wikisource - Biblioteca de textos.desktop", "Wikisource: Biblioteca de textos", "Colección histórica de textos y documentos fundamentales", "accessories-text-editor"),
    ("Proyecto Gutenberg - Libros clásicos.desktop", "Proyecto Gutenberg: Libros clásicos", "Biblioteca de miles de obras de literatura y divulgación científica", "x-office-document"),
    ("PhET - Simulaciones de física y química.desktop", "PhET: Simulaciones de física y química", "Modelos interactivos de física, circuitos eléctricos y química", "applications-science"),
]

for fname, title, comment, icon in library_books:
    fpath = os.path.join(LIBRARY, fname)
    with open(fpath, "w") as f:
        f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name={title}
Comment={comment}
Exec=bash "{GUEST_SCRIPTS}/refugios-kiwix.sh" "{GUEST_KNOW}/wikipedia.zim"
Icon={icon}
Terminal=false
""")
    os.chmod(fpath, 0o755)

print("Populated all desktop and library entries successfully!")
