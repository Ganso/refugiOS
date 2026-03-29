# Organización del Repositorio de Desarrollo y Contribución

Como estándar del universo open-source, de cara al flujo para bifurcaciones y un crecimiento metódico del trabajo del equipo, la plataforma de alojamiento preferente en Github establece una lógica distribuida.

Para comprender y expandir el gestor auto-armable desde la rama `main`, la siguiente matriz arquitectónica representa las jerarquías que el desarrollador enfrentará en este sistema en bruto.

## Árbol de Directorios del Repositorio

```text
refugiOS/
├── README.md                 <-- Landing Page. Instrucciones de uso e inicialización inicial
├── doc/                      <-- (Actualmente este y otros documentos conceptuales)
├── install.sh                <-- Entrypoint o "One-Liner" raíz a ejecutar en la terminal por el preparador del USB
├── scripts/
│   ├── 01_system_check.sh    <-- Detecta el espacio (df -B1) calculando umbral vital, y actualiza cache de apt libre.
│   ├── 02_i18n_setup.sh      <-- Ejecuta la adaptación estructural de Ubuntu, teclados y diccionarios globales L10N.
│   ├── 03_ui_menu.sh         <-- Despliegue de los UI por interfaz TUI interactivas (whiptail/zenity/dialog) pre-inyección.
│   ├── 04_downloader.sh      <-- Módulo agnóstico de redes CURL. Lógica de descarga automatizada de ZIMs base, Modelos SLM de IA y binarios AppImages.
│   ├── 05_apt_packages.sh    <-- Subsistema inyector dependencias offline. VLC, LibreOffice completo, Kolibri, compiladores y GCompris.
│   ├── 06_desktop_setup.sh   <-- El core de personalización XFCE. Quita bloatware inútil e inserta perfiles visuales, lanzadores directos (.desktop).
│   └── 07_vault_manager.sh   <-- Módulo criptográfico experto. Scripts subyacentes encargados de gestionar los bucles dev por LUKS (Crear, Abrir, Cerrar).
└── assets/
    ├── icons/                <-- Iconografía en formato escalable masivo (SVG) / altas trazas raster PNG (Cajas fuertes gráficas y Botones Big).
    └── desktop_templates/    <-- Plantillas de inyección cruda usadas en la conformación de atajos directos nativos e interfaces lanzadoras en XFCE Desk.
```

## Flujo Lógico de Implementación desde el *Entrypoint*

El objetivo primordial a retener por el contribuidor consiste en que el usuario ajeno nunca interactúe con el esqueleto.

1.  **Instanciación Externa Remota ("One-Liner"):**
    El Preparador se conectará abriendo la terminal negra de su recién flasheado XFCE Minimal recién arrancado con internet vía la red de comandos de unix:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/usuario/refugios/main/install.sh | bash
    ```
2.  **Encadenamiento Modular Secuencial:**
    El script maestro `install.sh` funcionará de orquestador o *proxy-booter*. Obtendrá sin permiso del entorno un volcado global del directorio `master` dentro del temporal unificado (`/tmp/refugios/`). Con un sistema ya anidado, forzará privilegios por elevación iterativa invocando como hilos uno a uno las funciones marcadas con la nomenclatura numérica en la capa interna de `/scripts`.
    
    *   Reconoce el entorno, valida el Hardware y las matemáticas de límite ISO con `df`, obligándoles bajo `whiptail` o `Zenity` a contestar el abanico vital de menús como encías de la instalación. Selecciona Wikipedia, Idioma y Paquetes de Ingeniería / Mapas.
3.  **Resolución de Acciones Clandestinas:** 
    Aceleradores como _El Gestor del Escritorio (`06_desktop_setup.sh`)_ modificarán en directo las directivas abstractas del usuario. Inyectando el comando de arranque de Kiwix tras bambalinas bajo el nombre de la variable interactiva asignada, por ejemplo enlazando la llamada bruta de terminal: `/opt/refugiOS/kiwix.appimage /opt/refugiOS/data/survivor_library_maxi.zim` para activarse con un doble toque iconográfico natural.

Este enfoque seccionales en módulos `bash` agiliza las pruebas lógicas para depurar partes sin alterar la experiencia visual o técnica del conjunto unitario en despliegue ininterrumpido.
