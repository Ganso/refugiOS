# Aplicaciones y Contenidos Incluidos, y Roadmap de Desarrollo

refugiOS incluye una selección de herramientas diseñadas para funcionar totalmente sin conexión a Internet. A continuación se detallan los módulos ya disponibles y los que planeamos añadir próximamente.

> [!IMPORTANT]
> **Internacionalización (i18n):** El instalador, los lanzadores y la documentación están disponibles en **español e inglés**. Más adelante se añadirán otros idiomas según el interés de la comunidad.
>
> **Migración de Documentación:** Estamos en proceso de migrar toda la documentación técnica y de usuario al formato **Wiki de GitHub** para facilitar su consulta y colaboración.

---

## 🚀 Módulos Actuales (Ya disponibles)

Estos componentes se instalan automáticamente o mediante el asistente de bienvenida:

### 1. Biblioteca y Enciclopedias Offline ([Kiwix](https://www.kiwix.org/))
Acceso a bases de datos masivas mediante el formato ZIM.
*   **Wikipedia en cinco niveles:** Ligera (~210 MB, artículos principales resumidos), esencial (~1,1 GB, artículos principales completos sin imágenes), esencial con imágenes (~3,8 GB), completa sin imágenes (~12 GB) y **completa con imágenes y multimedia** (~34 GB). Los tamaños son los de la Wikipedia en español; la inglesa es mucho mayor (~120 GB la completa). El instalador preselecciona la mayor que cabe holgadamente en tu unidad.
*   **Biblioteca por categorías:** Además de la Wikipedia, el instalador ofrece una biblioteca organizada en cuatro menús, con contenidos de acceso libre publicados por Kiwix:
    *   **Salud y medicina:** [WikiMed](https://www.kiwix.org/) (artículos médicos de Wikipedia), [WikEM](https://wikem.org/) (medicina de urgencias) y manuales de primeros auxilios y medicina de campaña.
    *   **Emergencias y supervivencia:** Guías postdesastre, agua potable, preparación de alimentos, nudos, [ScoutWiki](https://scoutwiki.org/) (en español), preguntas y respuestas de supervivencia al aire libre y [WikiHow](https://wikihow.com/).
    *   **Conocimiento práctico y reparaciones:** [iFixit](https://es.ifixit.com/), [Appropedia](https://www.appropedia.org/) (tecnología apropiada), [Energypedia](https://energypedia.info/) (energía solar y aislada), huerto, reparaciones domésticas, mecánica y radioafición.
    *   **Idioma, libros y educación:** [Wikcionario](https://es.wiktionary.org/) (diccionario), [Wikiviajes](https://es.wikivoyage.org/) (con guías de conversación en otros idiomas), Wikilibros, Wikisource, [Proyecto Gutenberg](https://www.gutenberg.org/) en español y las simulaciones científicas de [PhET](https://phet.colorado.edu/).
*   **Accesos en el escritorio:** La Wikipedia, WikiMed y WikiHow tienen icono propio en el escritorio; el resto de libros se reúnen en la carpeta **Biblioteca refugiOS** del escritorio, para que no se llene de iconos.
*   **Descargas verificadas:** Cada fichero se descarga mediante el *metalink* de Kiwix, que reparte la descarga entre varios mirrors y comprueba cada fragmento; si falla, se prueba cada mirror directamente y por último BitTorrent. El resultado se contrasta con la suma SHA-256 publicada, y una descarga interrumpida nunca se da por instalada: basta con volver a lanzar el instalador para reanudarla.
*   **Idioma:** 🌐 **Multilingüe.** El instalador descarga los archivos en el idioma que elijas y recurre a la versión inglesa cuando un libro no existe en él. Los libros que solo existen en inglés se marcan como tales en el menú.

### 2. Mapas y Navegación ([Organic Maps](https://organicmaps.app/))
Mapas vectoriales detallados con búsqueda y rutas offline.
*   **Contenidos:** Mapas de ciudades, senderos, fuentes de agua y hospitales.
*   **Mapas listos desde el instalador:** Puedes elegir en el propio instalador regiones habituales (España, Portugal, Europa entera, México, Colombia, Argentina, Chile, Perú, Venezuela, Brasil o Estados Unidos) y se descargan ya verificados en la carpeta de Organic Maps. Cualquier otra región se descarga después desde la propia aplicación, mientras haya conexión.
*   **Idioma:** 🌐 **Multilingüe.** La interfaz y los nombres de los mapas se adaptan a tu región.

### 3. Asistente de Inteligencia Artificial ([Llamafile](https://github.com/Mozilla-Ocho/llamafile))
Asistente inteligente privado que funciona 100% en tu ordenador local. Disponible en cinco niveles según la capacidad del dispositivo:
*   ⚪ **Mínimo:** [Qwen3-0.6B](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) (0.6B, Q4_K_M) — ~380 MB. Para dispositivos con recursos limitados (min. 4 GB RAM).
*   🟢 **Básico:** [Gemma-4-E4B-it](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF) (4B, Q4_K_M) — ~4.7 GB. Para PCs con 8 GB de RAM.
*   🟡 **Intermedio:** [Qwen3-8B](https://huggingface.co/unsloth/Qwen3-8B-GGUF) (8B, Q4_K_M) — ~4.8 GB. Para portátiles modernos con 8 GB de RAM.
*   🔴 **Avanzado:** [Qwen3-14B](https://huggingface.co/unsloth/Qwen3-14B-GGUF) (14B, Q4_K_M) — ~8.6 GB. Para PCs potentes con 16 GB de RAM.
*   ⚫ **Ultra:** [Gemma-4-26B-A4B-it](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) (26B MoE, Q4_K_M) — ~16.2 GB. Para estaciones de trabajo con 32 GB de RAM.
*   **Selector inteligente:** Al lanzar el asistente, un script detecta la RAM total y la VRAM de la GPU (NVIDIA/AMD), reserva un margen de seguridad estricto de 2 GB para el sistema operativo (evita swap a USB), y muestra un menú interactivo con solo los modelos instalados, preseleccionando automáticamente el más potente que el hardware puede ejecutar.
*   **Contexto de emergencia:** La interfaz de chat arranca con un mensaje de sistema en tu idioma que pide respuestas claras, breves y prácticas, prioriza los pasos urgentes en temas médicos o de seguridad y recuerda que el asistente no tiene acceso a Internet.
*   **Idioma:** 🌐 **Multilingüe.** Todos los modelos entienden y responden en más de 20 idiomas.

### 4. Bóvedas Criptográficas (LUKS)
Sistema de almacenamiento seguro y cifrado para datos sensibles.
*   **Estado:** Gestor interactivo unificado con un único icono de escritorio y menús basados en dialog.
*   **Características:** Soporte para múltiples bóvedas simultáneas con visualización de estado (abierta/cerrada), nombres personalizados, tamaños variables, creación, apertura, cierre y eliminación permanente.
*   **Automatización:** Detección inteligente de pendrives USB para sugerencia de tamaños e importación de datos automatizada.



### 5. Traductor sin conexión ([LocalTranslate](https://terslang.github.io/LocalTranslate/))
*   **Contenidos:** Traducción de textos entre más de 40 idiomas con los modelos neuronales de traducción de Firefox, que vienen dentro de la propia aplicación: no hay que descargar nada más.
*   **Instalación:** Opcional desde el instalador (~1,7 GB, comparte componentes con Organic Maps). Crea el icono **Traductor** en el escritorio.
*   **Complementos:** Las guías de conversación de Wikiviajes y el Wikcionario (en la biblioteca) ayudan con la pronunciación y el vocabulario.

### 6. Comprobar mi refugiOS
*   **Qué hace:** Un icono del escritorio revisa, sin conexión, que todo lo instalado está completo e intacto: descargas interrumpidas, ficheros dañados, accesos rotos, modelos de IA que no caben en la memoria del equipo, mapas que faltan y bóvedas dañadas. Termina con un informe y lo guarda en `~/refugiOS/check-report.txt`.
*   **Dos modos:** La comprobación rápida tarda unos segundos; la completa recalcula además las sumas de comprobación de cada fichero y puede tardar bastante en un pendrive lento.
*   **Cuándo usarla:** Al terminar la instalación, antes de guardar el dispositivo y después de clonarlo a otra unidad.

### 6b. Actualizar refugiOS
*   **Qué hace:** Un icono del escritorio busca, con conexión, ediciones nuevas de los libros instalados (o el libro en tu idioma si tenías la versión inglesa), versiones nuevas de Kiwix, del motor de IA y de las aplicaciones, revisiones de los modelos de IA y datos de mapa más recientes para las regiones que ya tenías. Muestra la lista con lo que ocupa cada cosa y aplica lo que elijas.
*   **Sin riesgo:** Cada versión nueva se descarga junto a la antigua y se verifica con su suma publicada; solo entonces se borra la anterior. Si una actualización falla o se corta, el dispositivo sigue exactamente como estaba y funcionando sin conexión. Las que no caben en el espacio libre se omiten.
*   **Cuándo usarla:** De vez en cuando, mientras haya conexión. No hace falta en ningún momento para que refugiOS funcione.

### 7. Herramientas de Trabajo Estándar
Programas esenciales para el día a día, adaptados para la máxima compatibilidad.
*   **Ofimática y Multimedia:** [LibreOffice](https://www.libreoffice.org/), [VLC](https://www.videolan.org/), [Evince](https://wiki.gnome.org/Apps/Evince) (PDF).
*   **Sistema y Navegación:** [Epiphany Browser](https://wiki.gnome.org/Apps/Web) (Navegador ligero), [Gedit](https://wiki.gnome.org/Apps/Gedit) (Editor de texto), [XFCE Terminal](https://docs.xfce.org/apps/terminal/start).
*   **Sincronización:** [Syncthing](https://syncthing.net/) (compartir archivos entre dispositivos sin necesidad de nube ni Internet).
*   **Ortografía:** Se instalan los diccionarios ortográficos, de separación silábica y de sinónimos del idioma elegido, que usan LibreOffice y el editor de textos.
*   **Idioma:** 🌐 **Multilingüe.** Todas las aplicaciones se instalan con el soporte de idioma local seleccionado.

### 8. Soporte de Hardware
*   **PC Estándar:** Optimizado para arquitecturas x86_64 (Intel/AMD) mediante AppImages y Flatpaks.
*   **Raspberry Pi:** 🍓 **Soporte Oficial.** El instalador detecta automáticamente dispositivos Raspberry Pi y utiliza paquetes nativos ARM para garantizar el rendimiento.

---

## 🔮 Roadmap (Módulos planeados a futuro)

Estamos trabajando para integrar estas potentes herramientas en próximas versiones:



### 2. Educación y Aprendizaje
*   **[Khan Academy Offline](https://es.khanacademy.org/):** Descarga de lecciones interactivas de matemáticas, ciencia y economía para todas las edades.
*   **Plataforma [Kolibri](https://learningequality.org/kolibri/):** Una completa biblioteca educativa con vídeos y ejercicios para escuelas en zonas remotas.

### 3. Bibliotecas de Literatura y Técnica
*   **[Project Gutenberg](https://www.gutenberg.org/):** ✅ **Ya disponible** la colección en español. La colección inglesa completa supera los 200 GB y está pendiente de ofrecerse por temas.
*   **[Survivor Library](http://www.survivorlibrary.com/):** Colección masiva de manuales sobre técnicas preindustriales (agricultura, forja, química básica).
*   **[Otras Bibliotecas para Kiwix](https://download.kiwix.org/zim/):** ✅ **Ya disponibles** diccionario, guías de viaje, libros de texto, reparaciones, energía y supervivencia (ver arriba). Se seguirán añadiendo más.

### 4. Análisis Avanzado con IA
*   **[AnythingLLM](https://useanything.com/) para Análisis de PDF:** Herramienta para "chatear" con tus propios documentos PDF locales.
*   **Expansión de Modelos:** Aumentar el catálogo de modelos disponibles (Vision, Codificación) según las capacidades del hardware.

### 5. Redes y Comunicación
*   **SDR (Radio Definida por Software):** Integración de herramientas como [Gqrx](https://gqrx.dk/) para recibir noticias o datos vía radio en situaciones de emergencia.

### 6. Ocio y entretenimiento
*   **Emuladores:** Sistemas retro con selección de juegos libres.
*   **Juegos:** Selección de juegos independientes de código abierto.

### 7. ❗ Mejoras técnicas
*   **Actualizador:** ✅ **Ya disponible** (icono *Actualizar refugiOS*, ver arriba). Pendiente: Avisar de forma automática de que hay actualizaciones cuando el equipo tiene conexión.
*   **Imágenes pregeneradas:** ✅ **Ya disponible.** Distribución de imágenes de disco listas para usar en distintos idiomas para un despliegue instantáneo desde [refugios.ganso.org](https://refugios.ganso.org/).
*   **Aceleración de IA por Hardware:** Optimización de GPU/NPU para modelos de IA locales.
*   **Soporte de más Hardware:** Ampliar el soporte de hardware para incluir más dispositivos y arquitecturas, incluyendo dispositivos que pueda poseer el usuario y necesite utilizar en situaciones de emergencia (sistemas de comunicación, wereables, etc.)
*   **Internacionalización:** Traducción del instalador y la documentación a más idiomas.