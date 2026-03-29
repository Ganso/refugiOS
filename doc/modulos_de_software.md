# Modulos de Software Principal y Bases de Conocimiento

Un componente central de toda experiencia con refugiOS radica en su arsenal intelectual. Descargado mediante instaladores dinámicos y comandos `curl`, `grep` y llamadas API a repositorios (Kiwix / Github) de modo que si las versiones estallan, el script recolecte automáticamente la última ISO del milisegundo de la compilación de forma ciega y perfecta, evitando fallos de URLs muertas (enlaces 404).

## 1. La Biblioteca Universitaria Offline (Formato ZIM)

Sostenido mediante el binario universal **Kiwix Desktop (Formato AppImage)**, un proyecto de alta compresión suizo multilingüe, uniendo archivos ZIM, un derivado extremo del empaquetado HTML.

*   **Wikipedia Principal (Generalista):** Se dispone el ZIM Máximo. Para la lengua inglesa pesa >115 GB y el compendio en idioma español suele medrar los ~50 GB de datos e incluye toda la librería textual junto con miniaturas ricas en fotografías topográficas, diagramas lógicos, etc. (`wikipedia_es_all_maxi.zim`). El usuario también dispondrá de la variante simplificada si sus pendrives son menores a 32GB (`_nopic.zim` o `_mini`).
*   **WikiMed (Emergencia Sanitaria Humana):** La enciclopedia de Medicina de alta celeridad (\~2 GB) respaldando una curaduría de emergencia que supera los 75.000 artículos en profundidad quirúrgica. Un hospital de campo indispensable.
*   **WikiHow (Supervivencia y Mecánica Práctica):** Toda la información de reensamblaje lógico en ilustraciones paso a paso sobre purificación térmica de agua o destilación y nudos de escalada (\~25 GB).
*   **Survivor Library (Biblioteca de Tecnología Pre-Industrial):** Enorme acervo anglosajón, concentrado históricamente en replicar saberes del Siglo XVIII y Siglo XIX: metalurgia primaria, agricultura sin abonos petroquímicos, o forjado, para el re-establecimiento de subsistencia material en entornos catastróficos (\~250 GB de tamaño requerido).

## 2. Navegación Topográfica Táctica (Mapas sin Servidores)

Se dota de la interfaz de la aplicación civil para Linux Desktop **Organic Maps**.

*   Es de código abierto absoluto (FOSS), concebida para una alta provisión de la intimidad operando sus algoritmos de ruteo _exclusivamente offline_.
*   Está sustentada en el mapeo de **OpenStreetMap** descargando el entorno cartográfico vectorizado del globo para permitir cálculos instantáneos ahorrando Gigabytes sobre versiones rasterizadas de la web.
*   Capaz de operar rastreo altitudinal, fuentes de agua, hospitales, o senderos montañosos lejanos. Con descargas parceladas por continentes o sub-naciones para adaptar el vector ISO a la variable USB elegida. El usuario indica la región a compilar en `install.sh`.

## 3. Inteligencia Artificial como Mecánico Local (Llamafile)

Desechamos implementaciones onerosas como Ollama y las pesadillas de dependencias anidadas de entornos virtuales Python, usando un ejecutable agnóstico y compilado globalmente: **Llamafile**. Se consolida tanto el motor lógico de inferencia binario (`llama.cpp`) como todo el archivo neuronal (.GGUF) dentro del mismo y único ejecutable. 

Funciona de "Doble-click", con rendimientos masivos para CPUs de viejos portátiles utilizando Small Language Models (SLMs) con una simple huella de ~4GB RAM base.
Se seleccionarán modelos compactos pero sofisticados:

*   **Microsoft Phi-3.5 Mini (3.8 Mil Millones Parámetros):** Especializado universalmente para procesar manuales. Brilla en tener uno de los _context windows_ (Ventanas de retención de atención) de hasta 128.000 tokens asimilando guías mecánicas inyectadas mediante lectura lateral, respondiendo e internamente traduciendo el español y otros 22 idiomas con razonamiento primario.
*   **DeepSeek R1 / Qwen (Versión de 1.5B):** Micro-modulo especialista para entornos restrictivos. Muy poderoso frente al peso del modelo y de extremada profundidad computacional algorítmica para matemáticas, química o lógica combinatoria básica a costa del carisma interactivo.

## 4. Estaciones de Trabajo y Educación Opcionales

Ya estemos bajo un árbol en ruta, o atrincherados, la terminal apt de Linux descargará al USB la paquetería de repos oficial por si se precisan. Un sistema necesita poder editar listas y escribir testamentos así como leer PDF ajenos.

*   **Paquetería Base Integrada por defecto:** `libreoffice` calc/writer para finanzas del grupo, `vlc` universal sin problemas de renderizado para videos extraídos, software como `evince` u otros (PDF) y visor de imágenes.
*   **Entornos de Sincronización (Syncthing):** Para crear redes de intercambio P2P mediante un punto de acceso LAN improvisado entre varios refugiados, comunicándonos sin internet de servidor central.
*   **Pack Desarrollo y Educación (A demanda):** Si en el menú se aceptan, instala constructores para software industrial o chips en placa: `build-essential`, `python3`, `git`, o la interfaz para niños escolares `gcompris` junto a repositorios FOSS extra de Khan Academy con plataformas educacionales como **Kolibri**.
