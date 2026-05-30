# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto se rige por [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
