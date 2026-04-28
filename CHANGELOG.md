# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto se rige por [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
