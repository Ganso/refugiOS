# Aplicaciones y Contenidos Incluidos, y Roadmap de Desarrollo

refugiOS incluye una selección de herramientas diseñadas para funcionar totalmente sin conexión a Internet. A continuación se detallan los módulos ya disponibles y los que planeamos añadir próximamente.

> [!IMPORTANT]
> **Internacionalización (i18n):** Actualmente, tanto el instalador como la documentación están disponibles **únicamente en español**. Próximamente se acometerá la traducción al inglés y, más adelante, a otros idiomas según el interés de la comunidad.
>
> **Migración de Documentación:** Estamos en proceso de migrar toda la documentación técnica y de usuario al formato **Wiki de GitHub** para facilitar su consulta y colaboración.

---

## 🚀 Módulos Actuales (Ya disponibles)

Estos componentes se instalan automáticamente o mediante el asistente de bienvenida:

### 1. Biblioteca y Enciclopedias Offline ([Kiwix](https://www.kiwix.org/))
Acceso a bases de datos masivas mediante el formato ZIM.
*   **Contenidos:** [Wikipedia](https://es.wikipedia.org/) (General), [WikiMed](https://www.kiwix.org/es/get-kiwix/download-content/) (Medicina), [WikiHow](https://www.wikihow.com/) (Guías prácticas).
*   **Idioma:** 🌐 **Multilingüe.** El instalador descarga los archivos específicamente en el idioma que elijas (es, en, fr, etc.).

### 2. Mapas y Navegación ([Organic Maps](https://organicmaps.app/))
Mapas vectoriales detallados con búsqueda y rutas offline.
*   **Contenidos:** Mapas de ciudades, senderos, fuentes de agua y hospitales.
*   **Idioma:** 🌐 **Multilingüe.** La interfaz y los nombres de los mapas se adaptan a tu región.

### 3. Asistente de Inteligencia Artificial ([Llamafile](https://github.com/Mozilla-Ocho/llamafile))
Asistente inteligente privado que funciona 100% en tu ordenador local. Disponible en cuatro niveles según la capacidad del dispositivo:
*   ⚪ **Mínimo:** [Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) (0.5B) — ~0.5 GB. Para dispositivos con recursos muy limitados (min. 1 GB RAM).
*   🟢 **Básico:** [Phi-4-mini](https://huggingface.co/microsoft/Phi-4-mini-instruct) (3.8B) — ~2.5 GB. Funciona en cualquier PC con 4 GB de RAM.
*   🟡 **Medio:** [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) (8B) — ~5 GB. Para portátiles modernos con 8 GB de RAM.
*   🔴 **Avanzado:** [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) (14B) — ~9 GB. Para PCs potentes con 16 GB de RAM.
*   **Selector automático:** Al lanzar el asistente, un script detecta la RAM disponible y recomienda el modelo adecuado.
*   **Idioma:** 🌐 **Multilingüe.** Todos los modelos entienden y responden en más de 20 idiomas.

### 4. Bóvedas Criptográficas (LUKS)
Sistema de almacenamiento seguro y cifrado para datos sensibles.
*   **Estado:** 🧪 **Prueba de Concepto (PoC).** El sistema es funcional y utiliza el estándar industrial LUKS, pero se encuentra en una fase primitiva de usabilidad.
*   **Limitaciones actuales:** Actualmente solo soporta una bóveda de tamaño fijo.
*   **Próximas mejoras:** Soporte para múltiples bóvedas, tamaños variables y una interfaz de gestión más intuitiva.


### 5. Herramientas de Trabajo Estándar
Programas esenciales para el día a día, adaptados para la máxima compatibilidad.
*   **Ofimática y Multimedia:** [LibreOffice](https://www.libreoffice.org/), [VLC](https://www.videolan.org/), [Evince](https://wiki.gnome.org/Apps/Evince) (PDF).
*   **Sistema y Navegación:** [Epiphany Browser](https://wiki.gnome.org/Apps/Web) (Navegador ligero), [Gedit](https://wiki.gnome.org/Apps/Gedit) (Editor de texto), [XFCE Terminal](https://docs.xfce.org/apps/terminal/start).
*   **Sincronización:** [Syncthing](https://syncthing.net/) (compartir archivos entre dispositivos sin necesidad de nube ni Internet).
*   **Idioma:** 🌐 **Multilingüe.** Todas las aplicaciones se instalan con el soporte de idioma local seleccionado.

### 6. Soporte de Hardware
*   **PC Terrestre:** Optimizado para arquitecturas x86_64 (Intel/AMD) mediante AppImages y Flatpaks.
*   **Raspberry Pi:** 🍓 **Soporte Oficial.** El instalador detecta automáticamente dispositivos Raspberry Pi y utiliza paquetes nativos ARM para garantizar el rendimiento.

---

## 🔮 Roadmap (Módulos planeados a futuro)

Estamos trabajando para integrar estas potentes herramientas en próximas versiones:

### 1. Ingesta automatizada en la bóveda personal
*   Mejorar los scripts para automatizar la importación de datos en las bóvedas personalizadas a partir de múltiples fuentes: Otros dispositivos USB, discos duros locales, etc.

### 2. Educación y Aprendizaje
*   **[Khan Academy Offline](https://es.khanacademy.org/):** Descarga de lecciones interactivas de matemáticas, ciencia y economía para todas las edades.
*   **Plataforma [Kolibri](https://learningequality.org/kolibri/):** Una completa biblioteca educativa con vídeos y ejercicios para escuelas en zonas remotas.

### 3. Bibliotecas de Literatura y Técnica
*   **[Project Gutenberg](https://www.gutenberg.org/):** Acceso a más de 70,000 libros clásicos de dominio público.
*   **[Survivor Library](http://www.survivorlibrary.com/):** Colección masiva de manuales sobre técnicas preindustriales (agricultura, forja, química básica).
*   **[Otras Bibliotecas para Kiwix](https://download.kiwix.org/zim/):** Diccionarios, física, matemáticas, educación, viajes, etc.

### 4. Análisis Avanzado con IA
*   **[AnythingLLM](https://useanything.com/) para Análisis de PDF:** Herramienta para "chatear" con tus propios documentos PDF locales.
*   **Expansión de Modelos:** Aumentar el catálogo de modelos disponibles (Vision, Codificación) según las capacidades del hardware.

### 5. Redes y Comunicación
*   **SDR (Radio Definida por Software):** Integración de herramientas como [Gqrx](https://gqrx.dk/) para recibir noticias o datos vía radio en situaciones de emergencia.

### 6. Ocio y entretenimiento
*   **Emuladores:** Sistemas retro con selección de juegos libres.
*   **Juegos:** Selección de juegos independientes de código abierto.

### 7. ❗ Mejoras técnicas
*   **Actualizador automático:** Sistema para actualizar componentes y bases de datos de forma incremental (aunque a día de hoy el instalador se puede lanzar todas las veces que sea necesario).
*   **Imágenes pregeneradas:** Distribución de imágenes de disco listas para usar en distintos idiomas para un despliegue instantáneo.
*   **Aceleración de IA por Hardware:** Optimización de GPU/NPU para modelos de IA locales.
*   **Soporte de más Hardware:** Ampliar el soporte de hardware para incluir más dispositivos y arquitecturas, incluyendo dispositivos que pueda poseer el usuario y necesite utilizar en situaciones de emergencia (sistemas de comunicación, wereables, etc.)