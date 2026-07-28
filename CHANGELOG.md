# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto se rige por [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.23] - 2026-07-28

### Añadido
- **Carpeta `media/` con todo el material gráfico:** Reúne el logotipo en sus distintos formatos y una colección de **cuarenta capturas de pantalla** de las aplicaciones principales (instalador, Wikipedia en Kiwix, Organic Maps, asistente de IA local y gestor de bóvedas), veinte en español y veinte en inglés, tomadas sobre el sistema real arrancado en una máquina virtual a 1920×1080. Cada subcarpeta tiene su propio índice bilingüe, y `media/` se enlaza desde ambos README. La autoría del logotipo ([Felipe Monge "PlayOnRetro"](https://x.com/PlayOnRetro)) se acredita en cada punto donde se enlaza.
- **Documentación de la suite de tests en `doc/`:** La guía de la suite pasa a formar parte de la documentación general del proyecto, en español ([Suite-de-Tests-ES.md](doc/Suite-de-Tests-ES.md)) e inglés ([Test-Suite-EN.md](doc/Test-Suite-EN.md)), enlazada desde el índice de la wiki y desde las guías de construcción de imagen, por ser un punto técnico que no afecta a todos los usuarios. `tests/README.md` queda como puntero a ambas.
- **Resolución configurable en las pruebas de arranque:** `tests/qemu_boot_check.py` acepta `--size` y arranca la máquina virtual a 1920×1080 por defecto, en lugar del tamaño heredado del adaptador.

### Cambiado
- **`logo/` pasa a ser `media/logo/`:** El instalador busca el fondo de escritorio en la ruta nueva y sigue aceptando la antigua en copias locales del repositorio anteriores a esta versión. Los sistemas ya instalados con una versión previa del instalador no encontrarán el fondo remoto y simplemente lo omitirán, sin afectar a ninguna otra parte de la instalación.

## [0.22] - 2026-07-28

Revisión crítica de los scripts del proyecto centrada en errores que rompían el
comportamiento de forma silenciosa. Todas las correcciones respetan el modelo de
seguridad existente y la capacidad de funcionamiento sin conexión.

### Corregido
- **La construcción de la imagen daba por bueno un chroot fallido:** El heredoc de `chroot` en `scripts/build_refugios.sh` se ejecutaba con `set -x` pero sin `set -e`, así que un fallo de `apt-get`, `grub-install` o `locale-gen` no lo detenía: continuaba hasta `apt-get clean`, cuyo código 0 se propagaba al script exterior. El build informaba de éxito y generaba una imagen que no arranca. Ahora el chroot aborta al primer fallo, su código de salida se comprueba explícitamente y el build termina con un mensaje descriptivo.
- **Restos de construcciones anteriores en la imagen:** `truncate` no vacía un fichero preexistente del mismo tamaño, por lo que se reparticionaba sobre el contenido previo. La imagen se elimina ahora antes de crearla, se hace `sync` antes de desasociar el dispositivo loop y se desmonta cualquier resto de un build interrumpido antes de empezar.
- **El "Developer Mode" de `install.sh` no tenía ningún efecto:** Las copias locales de `i18n.sh`, `i18n.py` e `install.py` se copiaban y acto seguido se sobrescribían con `wget` desde GitHub, de modo que los cambios locales solo podían probarse sin conexión a internet. Ahora, cuando el instalador se lanza desde una copia del repositorio, los ficheros locales tienen prioridad y no se descarga nada.
- **La contraseña de las bóvedas no se confirmaba:** `cryptsetup luksFormat` se invocaba con `--batch-mode`, que es precisamente la opción que desactiva la verificación de la contraseña. El usuario la tecleaba una sola vez y, ante una errata, la bóveda quedaba inaccesible para siempre sin ningún aviso. Se ha añadido `--verify-passphrase`, que anula esa desactivación manteniendo suprimida la confirmación de sobrescritura.
- **Las descargas grandes no podían completarse en conexiones lentas:** `download_with_aria2()` borraba el fichero parcial ante cualquier fallo, lo que anulaba `--continue=true`: un modelo de varios GB reiniciaba desde cero en cada intento y nunca terminaba. Los parciales se conservan ahora para poder reanudar, y el `timeout` absoluto pasa a ser solo una red de seguridad frente a una congelación, no un límite a la duración legítima de la descarga. Los ficheros pequeños mantienen el comportamiento anterior para que un script truncado no se confunda con uno válido.
- **El instalador podía quedarse colgado indefinidamente:** `fetch_url()` no tenía timeout, así que un mirror que aceptaba la conexión sin responder bloqueaba la instalación para siempre.
- **El "Developer Mode" tampoco alcanzaba a los scripts:** `fetch_script()` en `install.py` descargaba siempre desde GitHub y solo recurría a la copia local cuando la descarga fallaba, así que una copia del repositorio acababa instalando los scripts publicados en lugar de los suyos propios. Detectado ejecutando una instalación real en QEMU: el gestor de bóvedas del sistema instalado era el publicado, no el que se estaba probando.
- **Mensaje engañoso al fallar la creación de una bóveda:** Con la verificación de contraseña en su sitio, la causa habitual del fallo pasa a ser que las dos contraseñas no coincidan, pero el aviso hablaba de espacio en disco y permisos. Ahora se explica la causa real y se aclara que no se ha perdido nada.
- **Paso de fondo de escritorio sin traducir:** La clave `setting_wallpaper` no existía en `i18n.py` y durante la instalación se mostraba la clave en crudo al usuario.
- **Selección de versiones por orden alfabético:** Tanto `install.py` (AppImage de Kiwix) como `scripts/refugios-kiwix.sh` comparaban versiones como texto, eligiendo la 2.9 por encima de la 2.10. Ahora se comparan numéricamente. Además `refugios-kiwix.sh` descarta los AppImage sin permiso de ejecución.
- **`UnicodeEncodeError` en los menús del instalador:** `sanitize_for_dialog()` no se aplicaba en `multi_select_menu()`, `single_select_menu()` ni `simple_question()`, que son precisamente los que reciben las etiquetas traducidas de los módulos. Ahora todo texto pasa por el saneado antes de llegar a `dialog`.
- **El instalador terminaba con código 0 aunque fallaran módulos:** El wrapper del escritorio registraba «finalizado con código: 0» incluso con varios componentes fallidos. Ahora se devuelve un código distinto de cero cuando hay errores.
- **El idioma elegido por el usuario se ignoraba:** `scripts/i18n.sh` leía `~/.refugios_lang` y a continuación `$LANG` lo sobrescribía siempre. Ahora la elección persistida tiene prioridad y `$LANG` solo se consulta mientras no haya ninguna guardada. Además la función `t()` y sus cadenas se exportan, para que los lanzadores hijos muestren traducciones reales en lugar de la clave.
- **El motor de IA quedaba consumiendo memoria:** Al cerrar el lanzador, `llamafile` seguía residente; la única mitigación era un mensaje pidiendo al usuario que cerrase la ventana. Ahora un `trap` lo detiene siempre.
- **El navegador de la IA se abría contra un puerto muerto:** Se esperaba un `sleep 5` fijo, insuficiente para cargar un modelo grande desde una unidad lenta. Ahora se sondea el servidor y el navegador solo se abre cuando responde. Si `llamafile` no está instalado se avisa con un diálogo en vez de fallar con «No such file or directory».
- **`scripts/test_boot.sh` no encontraba la imagen:** Componía `refugios-base-TAMAÑO.img` mientras que el generador crea `refugios-base-TAMAÑO-IDIOMA.img`, así que pasar un tamaño nunca funcionaba. Acepta ahora `-s` y `-l` como `build_refugios.sh`, manteniendo la forma posicional antigua.
- **QEMU pedía 8 GB de RAM fijos:** El arranque de prueba fallaba en equipos modestos, justo el hardware al que apunta el proyecto. La memoria se calcula ahora a partir de la disponible, acotada a [2G, 8G].

### Añadido
- **Suite de tests automáticos (`tests/`):** Comprobación estática, tests unitarios de `install.py`, tests de los scripts Bash con dobles de los binarios externos, test del bootstrapper, test de bóvedas LUKS con ciclo completo y test de construcción de imagen con fallo inyectado. No requiere `sudo`: lo que necesita root se ejecuta en un contenedor Debian privilegiado. Se ejecuta con `bash tests/run_all.sh` y está documentada en la [Suite de Tests Automáticos](doc/Suite-de-Tests-ES.md).
- **Verificación de arranque por captura de pantalla:** `tests/qemu_boot_check.py` arranca una imagen construida sin interfaz gráfica y toma capturas en los instantes indicados, para comprobar el arranque completo sin intervención manual.
- **Nuevas claves de i18n:** `fail_i18n`, `no_tty`, `ai_llamafile_missing`, `ai_waiting_server`, `ai_server_died`, `ai_server_timeout`, `setting_wallpaper` y `vault_error_password` (EN + ES). Un test falla ahora si alguna clave usada en el código carece de traducción.

### Eliminado
- **Variable `USER_PASS` muerta** en `scripts/build_refugios.sh`: el usuario se crea con `passwd -d` y la variable no se usaba en ninguna parte.

## [0.21] - 2026-06-30

### Corregido
- **`FileNotFoundError` del gestor de bóvedas:** El instalador no encontraba `refugios-vault.py` ni en local ni en remoto y fallaba durante el despliegue. Se ha añadido validación previa que comprueba la existencia del archivo en disco antes de referenciarlo o ejecutarlo; si no está disponible, registra un log descriptivo, muestra un aviso al usuario mediante `d.msgbox` y omite el icono del Vault, pero permite que el resto de la instalación continúe sin lanzar un traceback.
- **`UnicodeEncodeError` (latin-1) en el resumen de instalación:** Al mostrar el resumen de errores mediante `d.msgbox`, el script fallaba al encontrar caracteres no compatibles con latin-1 (específicamente `•` U+2022), ya que la librería `dialog` codifica las cadenas en latin-1. Se ha sustituido el bullet por `-` y se han saneado los mensajes.
- **Script de Kiwix ausente sin aviso:** La llamada a `fetch_script("refugios-kiwix.sh")` ignoraba el valor de retorno, por lo que si el script faltaba no se notificaba al usuario y los accesos directos de las bases de conocimiento quedaban rotos silenciosamente. Ahora se comprueba su existencia y se avisa de forma descriptiva.
- **Script de IA ausente solo registrado en log:** Cuando faltaba `refugios-ai-selector.sh`, el aviso se registraba únicamente en el log sin notificación al usuario. Ahora se muestra también un diálogo descriptivo.

### Añadido
- **Función `sanitize_for_dialog()`:** Nueva utilidad en `install.py` que reemplaza caracteres Unicode tipográficos (`•`, `–`, `—`, comillas tipográficas, `…`) por equivalentes ASCII y codifica el resto a latin-1 con modo `replace`, garantizando compatibilidad con la librería `dialog`.
- **Validación previa de scripts críticos:** El instalador verifica ahora la existencia en disco de `refugios-vault.py`, `refugios-kiwix.sh` y `refugios-ai-selector.sh` tras intentar obtenerlos. Si alguno falta, se avisa al usuario (log + `d.msgbox`), se omite su icono de escritorio y la instalación continúa sin detenerse.
- **Nuevas claves de i18n:** `vault_script_missing`, `kiwix_script_missing` y `ai_script_missing` (EN + ES) con mensajes descriptivos que indican la causa y sugieren volver a ejecutar el instalador más adelante.
- **Limpieza de pantalla tras diálogos:** Se ejecuta `clear` en cada transición de diálogo a ejecución de comandos/instalación, en `install.py`, `scripts/refugios-vault.py` y `scripts/refugios-ai-selector.sh`, para que la salida de terminal quede más limpia entre fases.

### Cambiado
- **Resumen de errores con guiones en vez de bullets:** La lista de componentes fallidos en el mensaje final usa ahora `-` en lugar de `•` para evitar el `UnicodeEncodeError` con `dialog`.

## [0.20] - 2026-06-03

### Corregido
- **Archivos `.aria2` residuales:** La función `download_with_aria2()` ahora elimina siempre el archivo de control `.aria2` tras completar la descarga (éxito o fallo), y también borra archivos parciales si la descarga falla. Esto evita que queden archivos huérfanos que puedan confundir al sistema.
- **Etiqueta `[Instalado]` en menús:** El tag rojo que indica componentes ya instalados ahora aparece **antes** del nombre del elemento en los menús de multiselección (`d.checklist`) y selección individual (`d.menu`), mejorando la legibilidad visual.
- **Kiwix Flatpak no encuentra ejecutable:** El script `refugios-kiwix.sh` ahora detecta y soporta Kiwix instalado por Flatpak como fallback cuando no hay AppImage disponible. Usa `flatpak list --app` para verificar la instalación y `flatpak run org.kiwix.desktop` para ejecutarlo.
- **Kiwix Flatpak no puede abrir ZIM por línea de comandos:** Añadido `--filesystem="${ZIM_DIR}:ro"` al comando `flatpak run` para otorgar acceso explícito de solo lectura al directorio del archivo ZIM, resolviendo el problema del sandbox de Flatpak que bloqueaba el acceso a archivos pasados como argumento.
- **Kiwix no sigue enlaces simbólicos:** El script ahora resuelve los symlinks a rutas reales con `readlink -f` antes de pasar el archivo a Kiwix, ya que Flatpak sandbox no puede seguir enlaces simbólicos correctamente.
- **AppImage de Kiwix falla con "open dir error":** Añadida la variable de entorno `APPIMAGE_EXTRACT_AND_RUN=1` para ejecutar AppImages extrayéndolos primero, evitando problemas con FUSE en sistemas donde no está disponible o configurado correctamente.

## [0.19] - 2026-06-03

### Añadido
- **Modelo de IA ultra (5º modelo):** Nuevo modelo `ia_ultra` — Gemma-4-26B-A4B-it-UD-Q4_K_M (~16.2 GB). Ahora refugiOS soporta 5 niveles de modelo de IA: mínimo (0.6B), base (E4B), intermedio (8B), máximo (14B) y ultra (26B).
- **Sistema de descarga con aria2c:** Todas las descargas del instalador (Kiwix AppImage, Llamafile, modelos de IA, scripts internos, fondo de escritorio) usan ahora `aria2c` en lugar de `wget`. La nueva función `download_with_aria2()` ofrece 8 conexiones paralelas, timeout estricto por descarga (evita congelaciones), y reintentos automáticos.
- **Timeout absoluto en descargas:** La función `download_with_aria2()` envuelve cada descarga con el comando `timeout` de Linux, garantizando que ninguna descarga puede bloquear la instalación indefinidamente. Si se supera el límite, el instalador salta al siguiente método de la cascada (Flatpak → APT).
- **Módulo de IA dinámico:** El instalador lee el diccionario `AI_MODEL_CONFIG` de forma completamente dinámica, sin límite fijo de modelos. Cualquier número de modelos puede añadirse al diccionario y el sistema los detectará, comprobará cuáles están descargados y permitirá seleccionar e instalar cualquiera de ellos.

### Cambiado
- **Nuevos modelos de IA (5 modelos actualizados):**
  | ID | Modelo | Tamaño real | RAM mínima |
  |---|---|---|---|
  | `ia_min` | Qwen3-0.6B-Q4_K_M | ~380 MB | 4 GB |
  | `ia_base` | gemma-4-E4B-it-Q4_K_M | ~4.7 GB | 8 GB |
  | `ia_med` | Qwen3-8B-Q4_K_M | ~4.8 GB | 8 GB |
  | `ia_max` | Qwen3-14B-Q4_K_M | ~8.6 GB | 16 GB |
  | `ia_ultra` | gemma-4-26B-A4B-it-UD-Q4_K_M | ~16.2 GB | 32 GB |
- **URLs de modelos actualizadas:** Todos los modelos ahora se descargan directamente desde el repositorio de **unsloth** en HuggingFace (CDN más rápido y fiable que bartowski).
- **Selector de IA reescrito:** `refugios-ai-selector.sh` ahora detecta RAM total y VRAM (NVIDIA/AMD), resta un margen de seguridad estricto de 2 GB para el SO (evita swap a USB), muestra un menú `dialog` con solo los modelos instalados, y preselecciona automáticamente el modelo más potente que el hardware puede ejecutar.
- **Eliminada dependencia de `wget`:** Ya no se instala ni se usa `wget` en el sistema. `aria2c` cubre todas las necesidades de descarga.
- **Tamaños de modelos corregidos:** Los valores `size_mb` en `AI_MODEL_CONFIG` han sido ajustados a los tamaños reales medidos desde la API de HuggingFace (cambios significativos: gemma-4-E4B de 2.5→4.7 GB, Qwen3-14B de 8.2→8.6 GB, gemma-4-26B de 14.8→16.2 GB).

### Corregido
- **Congelación de instalación por descargas lentas:** El problema por el que la descarga del AppImage de Kiwix (u otros archivos grandes) podía bloquear la instalación indefinidamente ha sido resuelto mediante timeouts estrictos y la cascada de fallback a Flatpak/APT.
- **Symlinks de modelos incompletos:** Los archivos `.aria2` residuales de descargas interrumpidas ya no se enlazan como modelos válidos.

## [0.18] - 2026-06-02

### Corregido
- **Detección de AVX2 en el motor de IA:** El script `refugios-ai-selector.sh` comprueba ahora `/proc/cpuinfo` para detectar si el procesador soporta AVX2. En procesadores sin esta instrucción (como algunas CPUs antiguas o ARM), se pasa el parámetro `-ngl 0` a llamafile para desactivar la descarga GPU, evitando así errores fatales en tiempo de ejecución.
- **Actualización del selector de IA sin modelos nuevos:** La llamada a `fetch_script("refugios-ai-selector.sh")` se ha movido fuera del bloque `if ai_selected:` en `install.py`, de modo que el script del selector se actualiza siempre al ejecutar la instalación, incluso si el usuario no selecciona modelos de IA.

### Cambiado
- **Información de tamaño en menús de selección:** Los diálogos de Ofimática y Cartografía muestran ahora el tamaño estimado de cada componente (~1.3 GB para LibreOffice/VLC/Syncthing/Evince, ~2.1 GB para Organic Maps), permitiendo al usuario tomar una decisión informada antes de instalar.

## [0.17] - 2026-05-30

### Añadido
- **Log de instalación unificado:** Las funciones de log del instalador (`log_info`, `log_err`, `log_success`) escriben ahora simultáneamente en consola y en el archivo `/tmp/refugios-install.log`, permitiendo revisar el historial completo de la instalación a posteriori.
- **Medición de espacio por fases:** El instalador mide y registra en el log el espacio ocupado en disco al finalizar cada fase de instalación (utilidades base, Kiwix Desktop, bases de conocimiento ZIM, mapas offline, modelos de IA y bóveda de seguridad), así como el total acumulado al concluir.
- **Espacio total en mensaje de fin:** El mensaje de finalización de la instalación muestra ahora el espacio total ocupado en MB durante el proceso.
- **Estimación de espacio antes de instalar:** El instalador calcula el espacio estimado que ocupará la selección del usuario (sin contar componentes ya instalados) y lo muestra en el diálogo de confirmación previo a la instalación.
- **Aviso de espacio insuficiente:** Si el espacio libre disponible es inferior al 120% del tamaño estimado de la instalación, el diálogo de confirmación muestra una **ALERTA CRÍTICA** destacada, advirtiendo al usuario de que la instalación puede fallar.

### Cambiado
- **Tamaño real de Wikipedia NoPics:** La estimación interna y la etiqueta visible al usuario de Wikipedia sin imágenes (`all_nopic`) han sido actualizadas de ~9.5 GB a **~11.5 GB**, reflejando el tamaño real medido en instalaciones reales.
- **Script wrapper de instalación mejorado:** El script `/usr/local/bin/refugios-install-wrapper.sh` generado por el instalador es ahora idéntico al inyectado por `build_refugios.sh`: incluye registro de inicio/fin en el log, mensajes de estado al comprobar la conexión, y diálogo de error gráfico (`zenity`) o bloque de texto en consola si no hay conectividad, con textos internacionalizados según el idioma del sistema.
- **Corrección gramatical en bienvenida:** El mensaje de bienvenida al primer arranque ahora dice correctamente «en un dispositivo de X GB» en lugar de «en un X GB» (tanto en español como en inglés).

## [0.16] - 2026-05-29

### Añadido
- **Fondo de escritorio:** Añadido nuevo fondo de escritorio, con configuración para Raspberry OS y XFCE durante la instalación.

## [0.15] - 2026-05-28

### Añadido
- **Gestor unificado de Bóvedas:** Los tres iconos de escritorio separados (Crear, Abrir, Cerrar bóveda) han sido reemplazados por una única aplicación interactiva con menús `dialog`. El nuevo gestor muestra todas las bóvedas existentes con su estado (Abierta/Cerrada) y tamaño, y permite crear, abrir, cerrar o eliminar bóvedas desde un solo punto de acceso. Al seleccionar una bóveda se ofrece un submenú contextual con las acciones disponibles según su estado.
- **Eliminación de bóvedas:** Nueva funcionalidad para eliminar permanentemente una bóveda cerrada, con confirmación de seguridad. No se permite eliminar bóvedas abiertas.
- **Icono de instalación persistente:** El instalador crea ahora el lanzador de escritorio "Completar instalación de refugiOS" y su script wrapper (`/usr/local/bin/refugios-install-wrapper.sh`) si no existen, permitiendo al usuario añadir nuevos componentes en cualquier momento sin depender de la imagen base.
- **Limpieza de iconos obsoletos:** El instalador detecta y elimina automáticamente los iconos de escritorio pertenecientes a versiones anteriores del sistema (actualmente los tres antiguos iconos de gestión de bóvedas), evitando accesos directos huérfanos tras una actualización.
- **Tres niveles de pre-configuración:** El instalador ahora distingue tres umbrales de almacenamiento en lugar de dos: modo ligero (< 30 GB), modo estándar (30-70 GB) y modo enriquecido (≥ 70 GB), con selecciones automáticas consecuentes para cada nivel.

### Cambiado
- **Tamaños reales de componentes:** Las estimaciones de tamaño en el instalador y la documentación han sido actualizadas con los valores reales medidos sobre los ficheros instalados: Qwen2.5-0.5B (~380 MB), Phi-4-mini (~2.3 GB), Qwen3-8B (~4.7 GB), Qwen3-14B (~8.4 GB), WikiMed (~620 MB), WikiHow (~20 GB).
- **Umbral de modo ligero:** Elevado de 25 GB a 30 GB para reflejar mejor los requisitos reales de los componentes.
- **Tabla de capacidades en documentación:** La tabla de capacidad/contenido en las guías de elección de medio de instalación ha sido actualizada para reflejar con mayor precisión qué contenido cabe en cada tamaño de dispositivo (16/32/64/128 GB).

### Corregido
- **Certificación de iconos de escritorio:** Resuelto el bug por el que los iconos `.desktop` no se marcaban como fiables en XFCE. La causa era doble: (1) la imagen base no incluía `libglib2.0-bin` (que proporciona el comando `gio`, indispensable para establecer `metadata::xfce-exe-checksum`), y (2) el mecanismo de certificación establecía metadatos innecesarios (`metadata::trusted`, xattr) que XFCE no reconocía. Ahora la imagen base incluye `libglib2.0-bin` y `certify_icon` solo establece `metadata::xfce-exe-checksum`, que es el único campo que XFCE verifica.

### Cambiado
- **Instalación de paquetes base individualizada:** Los paquetes del sistema base se instalan ahora uno a uno en lugar de en un único comando `apt-get install`, para que un paquete inexistente en la distribución actual (ej. `language-selector-common` en Debian) no impida la instalación del resto.
- **Usuario sin contraseña:** En la imagen base, el usuario `refugios` se crea ahora sin contraseña de login (`passwd -d`), evitando el bloqueo de pantalla por inactividad que requería introducir una clave que el usuario no conoce.
- **Bloqueo de pantalla deshabilitado:** La imagen base desactiva el salvapantallas y el bloqueo automático de pantalla de XFCE mediante configuración global de `xfce4-screensaver`.
- **Base Debian Trixie:** La imagen base ha pasado de Debian Bookworm a Debian Trixie (testing), proporcionando paquetes más recientes y mejor soporte de hardware.

## [0.14] - 2026-05-27

### Añadido
- **Wikipedia con imágenes:** Nueva opción de descarga "Wikipedia Total" (`all_maxi`) que incluye la Wikipedia completa con todas las imágenes y contenido multimedia (~38 GB). Anteriormente solo estaban disponibles las versiones sin imágenes (Lite y NoPics). El instalador ahora ofrece tres niveles de Wikipedia: Lite (artículos destacados, ~73 MB), NoPics (texto completo sin imágenes, ~9.5 GB) y Total (completa con imágenes, ~38 GB).

## [0.13] - 2026-05-26

### Añadido
- **Sistema de construcción de imagen de sistema:** Nuevo script `scripts/build_refugios.sh` que genera automáticamente una imagen de disco base de refugiOS desde cero usando debootstrap (Debian Bookworm + XFCE), sin depender de una ISO de Xubuntu preexistente. Incluye particionado GPT (EFI + ROOT), instalación de GRUB en modo removible, autologin en LightDM, autoexpansión del disco en el primer arranque, lanzador del instalador en el escritorio, popup de bienvenida y personalización del escritorio XFCE.
- **Script de prueba de arranque UEFI:** Nuevo script `scripts/test_boot.sh` que permite verificar el arranque de la imagen generada mediante QEMU con firmware OVMF, detección automática de KVM y soporte multi-distribución para las rutas de firmware UEFI.
- **Documentación del sistema de construcción:** Nuevas guías exhaustivas en español (`doc/Construccion-Imagen-Sistema-ES.md`) e inglés (`doc/System-Image-Build-EN.md`) detallando requisitos, proceso de construcción, prueba de arranque, volcado a dispositivo, estructura de particiones, scripts inyectados, bug conocido de iconos de escritorio y flujos de trabajo recomendados.
- **Guía de elección del medio de instalación:** Nuevo documento compartido en español (`doc/Eleccion-Medio-Instalacion-ES.md`) e inglés (`doc/Choosing-Installation-Media-EN.md`) que centraliza la información sobre elección de dispositivo físico (pendrive vs SSD, capacidades, presupuestos, consejos de compra), anteriormente duplicada en la guía de XUbuntu. Incluye una tabla de implicaciones según el método de instalación elegido.

### Cambiado
- **Reestructuración de la documentación de instalación:** La sección "Elección del hardware" ha sido extraída de las guías de instalación en XUbuntu (ES/EN) y migrada a la nueva guía dedicada de elección del medio de instalación, ya que aplica igualmente a las imágenes de sistema nativas. Las guías de XUbuntu ahora referencian la nueva guía y tienen la numeración de secciones actualizada.

## [0.12] - 2026-05-07

### Añadido
- **Soporte de múltiples mirrors para ZIM:** Los entries en `KNOWLEDGE_CONFIG` ahora pueden tener `search_urls` (lista) además de `search_url`. Si la descarga directa desde un mirror falla, se prueba el siguiente en orden antes de caer a torrent.
- **Fallback a torrent en descargas ZIM:** Si la descarga directa agota todos los mirrors, el instalador intenta automáticamente la descarga por BitTorrent como respaldo antes de reportar el error.
- **Cascada de métodos de instalación robustecida:** Ahora si la descarga de un AppImage falla (wget retorna error), el instalador continúa probando Flatpak y APT en lugar de asumir éxito.

### Cambiado
- **WikiHow con triple mirror:** WikiHow ahora usa `cdimage.debian.org`, `mirror.netcologne.de` y `mirror-sites-ca.mblibrary.info` como fuentes de descarga, probándose en orden.

## [0.11] - 2026-04-28

### Añadido
- **Sistema de información de errores:** Implementado un sistema de registro de fallos no fatales con soporte multi-idioma (ES/EN) para mostrar un resumen detallado al finalizar la instalación si algún componente falló.

### Cambiado
- **Mejora en la robustez del Instalador:** El proceso de instalación ya no se detiene ante errores individuales de descarga o instalación. Los fallos se acumulan permitiendo que el despliegue continúe con el resto de componentes.
- **Certificación de iconos optimizada:** El instalador ahora solo intenta certificar y marcar como confiables los iconos creados durante la sesión actual, ignorando archivos preexistentes en el escritorio y evitando así errores de permisos.

## [0.10] - 2026-04-16

### Añadido
- **Rediseño Completo del Sistema de Bóvedas:** Migración de los scripts de gestión de bóvedas (`create`, `open`, `close`) a un sistema unificado en Python (`refugios-vault.py`).
- **Nueva Interfaz TUI (Dialog):** Los menús de gestión de bóvedas ahora utilizan `python-dialog`, ofreciendo una experiencia visual y consistente con el resto del sistema.
- **Soporte Multi-bóveda:** Posibilidad de crear, abrir y cerrar múltiples bóvedas con nombres personalizados.
- **Detección Automática de USB:** El creador de bóvedas detecta pendrives conectados, sugiere un tamaño óptimo (1.5x el espacio ocupado) y permite importar los datos automáticamente al finalizar la creación.
- **Integración con el Escritorio:** Al abrir una bóveda, se crea dinámicamente un icono en el escritorio con el nombre de la misma que desaparece automáticamente al cerrarla.
- **Seguridad Mejorada:** Implementada reserva del 10% del espacio libre en el sistema raíz para evitar bloqueos del sistema y añadidas recomendaciones de seguridad localizadas para la elección de contraseñas.

## [0.09] - 2026-04-09

### Añadido
- **Documentación completa en Inglés:** Toda la documentación se ha traducido al inglés.
- **Soporte multilingue en la instalación:** Todos los scripts soportan inglés y español.

## [0.08] - 2026-04-08

### Añadido
- **Nuevo logo del proyecto:** Gracias a [Felipe Monge "PlayOnRetro"](https://x.com/PlayOnRetro) por el diseño del logo.
- **Readme en Inglés:** Gracias a [levonk](https://github.com/levonk) por la versión inicial.

## [0.07] - 2026-04-08

### Añadido
- **Clarificación de Idioma e Internacionalización:** Se ha añadido información explícita en el README y en el Roadmap sobre el estado actual del proyecto (solo español) y los planes futuros para el soporte de inglés.
- **Migración a Wiki:** Se anuncia el inicio de la migración de la documentación técnica al formato Wiki de GitHub.

### Cambiado
- **Reestructuración de Documentación:** El archivo `doc/modulos_de_software.md` ha sido renombrado a `doc/modulos_y_roadmap.md` para reflejar mejor su contenido y se han actualizado todos los enlaces internos.

## [0.06] - 2026-04-07

### Cambiado
- **Nueva Interfaz de Usuario:** El instalador ahora utiliza la librería `python-dialog` para mostrar menús interactivos, cuadros de diálogo de diagnóstico y selectores múltiples. Esto hace que la experiencia de instalación sea mucho más amigable, visual e intuitiva que la versión anterior basada en línea de comandos.

## [0.05] - 2026-04-06

### Añadido
- **Soporte Oficial Raspberry Pi:** Raspberry Pi 3B+ con Raspberry Pi OS (64-bit, Wayland) ya es una plataforma certificada. Eliminados todos los avisos de compatibilidad experimental.
- **Modelo Raspberry Pi en el diagnóstico:** El instalador detecta y muestra la cadena exacta del modelo de Raspberry Pi desde `/proc/device-tree/model` al inicio.
- **Scripts intermediarios de lanzado:** Todos los iconos del escritorio ahora invocan scripts en `~/refugiOS/Scripts/` que ejecutan la lógica en tiempo real al lanzarse:
  - `refugios-maps.sh`: Detecta si la RPi es anterior a la versión 4 y activa automáticamente renderizado por software para Organic Maps (`LIBGL_ALWAYS_SOFTWARE=1`).
  - `refugios-kiwix.sh`: Detecta el binario de Kiwix disponible (sistema, AppImage) y lo usa para abrir el recurso ZIM especificado.
- **Guía de instalación para Raspberry Pi:** Nuevo documento `doc/instalacion_raspberry.md` con instrucciones, hardware recomendado, tabla de diferencias con la versión XUbuntu, y referencia al Raspberry Pi Imager oficial.
- **Certificación de lanzadores mejorada:** La lógica de confianza de los `.desktop` ahora cubre GIO (XFCE, GNOME, Wayland), checksum XFCE, y fallback con atributos extendidos. También crea automáticamente `libfm.conf` con `quick_exec=1` si no existe (necesario para evitar diálogos de advertencia en PCManFM / Raspberry Pi OS con Wayfire).

### Cambiado
- **`installpy.sh` renombrado a `install.sh`:** El instalador Python es ahora el oficial y único punto de entrada. El antiguo instalador shell se ha archivado en `old/`.
- **`doc/instalacion_manual.md` renombrado a `doc/instalacion_xubuntu.md`:** Refleja que esa guía es específica para XUbuntu.
- **Todos los modelos y bases de conocimiento centralizados en constantes** `KNOWLEDGE_CONFIG` y `AI_MODEL_CONFIG` en la cabecera de `install.py`.
- **Restauración inteligente de iconos:** Al final de cada instalación, `sync_resources()` recorre todo el disco y recrea los iconos faltantes para cualquier recurso ya descargado, incluso si no fue seleccionado en la sesión actual.

## [0.04] - 2026-04-03


### Añadido
- **Instalador Python (Experimental)**: Nueva versión del instalador reescrita en Python (`install.py`) y lanzada a través de `installpy.sh`. Separa scripts internos, soluciona advertencias del escritorio (XFCE/PCManFM), mejora notablemente los menús interactivos permitiendo omitir (0) y hacer múltiples selecciones simultáneas, y resuelve conflictos idiomáticos locales. Esta versión es **más compatible con entornos ARM y Raspberry Pi OS**, aunque carece de testeos extensos de calidad total (se anima a la comunidad a probarla).

## [0.03] - 2026-04-02

### Añadido
- **Soporte Hardware**: Pruebas preliminares en **Raspberry Pi 3B+**. El script de instalación es funcional tras resolver dependencias críticas, aunque con limitaciones importantes de arquitectura y rendimiento.

### Cambiado
- **Instalador**: Eliminada la dependencia obligatoria de `language-selector-common` para mejorar la compatibilidad con Raspberry Pi OS (Debian).
- **Instalador**: Dividida la instalación de paquetes en bloques de máximo 5 unidades para evitar errores por falta de memoria (OOM) en dispositivos con poca RAM.
- **Instalador**: Oculta la "Advertencia de Persistencia" cuando se detecta hardware Raspberry Pi.
- **Escritorio**: Configuración automática de `pcmanfm` para evitar el diálogo de confirmación al ejecutar lanzadores.

### Errores conocidos (Raspberry Pi)
- **Kiwix**: No funcional. Requiere una versión de Kiwix Desktop compilada para arquitectura ARM (actualmente descarga x86_64).
- **Organic Maps**: No funcional por errores en la inicialización de OpenGL ES3/Framebuffer. Pendiente de optimización de drivers/entorno.
- **Inteligencia Artificial**: Modelos como Phi-4-mini no han podido ser validados satisfactoriamente debido a las severas limitaciones de RAM (1GB) de la Raspberry Pi 3B+.

## [0.02] - 2026-04-01

### Añadido
- **Instalador**: Opción para omitir la descarga de Wikipedia (grande o pequeña) en `install.sh`.
- **Documentación**: Sección en "Módulos de Software" sobre la futura migración del instalador a Python para mejorar su mantenimiento, así como otras mejoras propuestas.

### Cambiado
- **Instalador**: Lógica de descarga ZIM optimizada para ser totalmente condicional y limpiar enlaces simbólicos previos si se omiten módulos. Mejoras en el sistema de menús.
