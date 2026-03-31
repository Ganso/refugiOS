# Aplicaciones y Contenidos Incluidos (Actual y Futuro)

refugiOS incluye una selección de herramientas diseñadas para funcionar totalmente sin conexión a Internet. A continuación se detallan los módulos ya disponibles y los que planeamos añadir próximamente.

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
Asistente inteligente privado que funciona 100% en tu ordenador local. Disponible en tres niveles de potencia según la capacidad del PC:
*   🟢 **Básico:** [Phi-4-mini](https://huggingface.co/microsoft/Phi-4-mini-instruct) (3.8B) — ~2.5 GB. Funciona en cualquier PC con 4 GB de RAM.
*   🟡 **Medio:** [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) (8B) — ~5 GB. Para portátiles modernos con 8 GB de RAM.
*   🔴 **Avanzado:** [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) (14B) — ~9 GB. Para PCs potentes con 16 GB de RAM.
*   **Selector automático:** Al lanzar el asistente, un script detecta la RAM disponible y recomienda el modelo adecuado.
*   **Idioma:** 🌐 **Multilingüe.** Todos los modelos entienden y responden en más de 20 idiomas.


### 4. Herramientas de Trabajo Estándar
Programas esenciales para el día a día.
*   **Contenidos:** [LibreOffice](https://www.libreoffice.org/) (documentos y tablas), [VLC](https://www.videolan.org/) (vídeo/audio), [Evince](https://wiki.gnome.org/Apps/Evince) (PDF) y [Syncthing](https://syncthing.net/) (compartir archivos sin red).
*   **Idioma:** 🌐 **Multilingüe.** Todas las aplicaciones se instalan con el soporte de idioma local seleccionado.

---

## 🔮 Roadmap (Módulos planeados a futuro)

Estamos trabajando para integrar estas potentes herramientas en próximas versiones:

### 1. Educación y Aprendizaje
*   **[Khan Academy Offline](https://es.khanacademy.org/):** Descarga de lecciones interactivas de matemáticas, ciencia y economía para todas las edades.
    *   **Idioma:** 🌐 **Multilingüe** (disponible en español e inglés).
*   **Plataforma [Kolibri](https://learningequality.org/kolibri/):** Una completa biblioteca educativa con vídeos y ejercicios para escuelas en zonas remotas.
    *   **Idioma:** 🌐 **Multilingüe.**

### 2. Bibliotecas de Literatura y Técnica
*   **[Project Gutenberg](https://www.gutenberg.org/):** Acceso a más de 70,000 libros clásicos de dominio público en formato electrónico.
    *   **Idioma:** 🌐 **Multilingüe** (especialmente rico en inglés, francés y alemán, con miles de títulos en español).
*   **[Survivor Library](http://www.survivorlibrary.com/):** Una colección masiva de manuales sobre técnicas preindustriales (agricultura, forja, química básica).
    *   **Idioma:** 🇺🇸 **Principalmente Inglés.**

### 3. Análisis Avanzado con IA
*   **[AnythingLLM](https://useanything.com/) para Análisis de PDF:** Una herramienta que permite "chatear" con tus propios documentos PDF locales. Podrás preguntarle a la IA sobre manuales técnicos de 500 páginas y obtener respuestas instantáneas.
    *   **Idioma:** 🌐 **Multilingüe.** Funciona con documentos en cualquier idioma que entienda el modelo base.

### 4. Redes y Comunicación
*   **Estaciones de Radio Digital ([SDR](https://gqrx.dk/)):** Integración de herramientas para conectar el ordenador a radios de onda corta (SDR) para recibir noticias o datos en situaciones de colapso total.
    *   **Idioma:** 🌐 **Agnóstico al idioma.**

### 5. Otras funcionalidades
*   **Actualización:** Aunque los actuales scripts están pensados para poder ejecutarse varias veces, un script de autualización podría acelerar mucho este proceso, especialmente para actualizar rápidamente las carpetas de datos encriptados.
*   **Imágenes pregeneradas para distintos idiomas y tamaños de dispositivo:** Para un despliegue rápido sin pasar por todo el proceso de descarga y configuración.
*   **Hardware adicional:** Soporte de hardware adicional. Especialmente de GPU o NPU para aceleración de los modelos de IA locales.