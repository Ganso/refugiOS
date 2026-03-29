# **Plan Maestro de Ingeniería: Proyecto "refugiOS" (Estación de Supervivencia Digital)**

## **1\. Visión General y Experiencia del Usuario**

El presente documento constituye la hoja de ruta técnica y arquitectónica para el equipo de desarrollo encargado de construir el sistema. Para garantizar que las decisiones de ingeniería estén alineadas con el producto final, a continuación se define el comportamiento del sistema desde la perspectiva del usuario final.

### **1.1. Propósito, Casos de Uso y Nomenclatura**

El nombre **refugiOS** nace de la fusión conceptual entre la palabra "Refugio" y el acrónimo informático "OS" (Sistema Operativo). A diferencia de términos como "navaja suiza" que pueden evocar un uso táctico o agresivo, un *refugio* transmite la verdadera esencia del proyecto: un santuario o búnker digital seguro, inexpugnable e inalterable, destinado a salvaguardar el conocimiento humano, la identidad y la vida frente al colapso de las infraestructuras externas.  
refugiOS está diseñado como una herramienta extrema de "plug-and-play" offline.1 Sus casos de uso abarcan la preparación ante desastres naturales severos, apagones globales prolongados de la red eléctrica o de telecomunicaciones, asistencia en zonas rurales sin infraestructura, y protección de información para periodistas o activistas en entornos hostiles. Su objetivo es convertir cualquier ordenador de consumo disponible (incluso hardware obsoleto rescatado) en un centro de conocimiento, navegación e inteligencia artificial completamente autárquico.

### **1.2. Experiencia de Instalación (El "Preparador")**

El proceso de creación del dispositivo debe ser intuitivo y desatendido, exigiendo conocimientos técnicos mínimos por parte del usuario:

1. **Preparación del Medio:** El usuario adquiere un USB de alta capacidad y rendimiento. Utilizando su sistema habitual, el usuario graba una imagen ISO estándar de Xubuntu con persistencia, o bien realiza una instalación nativa completa directamente sobre el disco externo.  
2. **Ejecución del Instalador:** El usuario arranca su ordenador desde ese nuevo USB. Abre la terminal e introduce un único comando (un *One-Liner* proporcionado en nuestro repositorio).  
3. **Configuración Interactiva:** El script toma el control y lanza un asistente visual con menús. Detecta el espacio libre real del USB y pregunta al usuario:  
   * *¿Cuál es tu idioma preferido?* (Ajustando todo el sistema operativo a esa selección).  
   * *¿Qué módulos de conocimiento deseas?* (Mostrando opciones viables según el espacio: Wikipedia completa vs. mini, manuales médicos, biblioteca de supervivencia).  
   * *¿Qué región cartográfica necesitas?*  
   * *¿Deseas instalar paquetes adicionales?* (Herramientas ofimáticas, programación, educación).  
4. **Generación de la Bóveda Privada:** Una vez descargado el conocimiento, el asistente invita al usuario a conectar el pendrive donde tenga temporalmente sus documentos sensibles (pasaporte, historiales médicos, escrituras). El sistema pide una clave maestra, absorbe esa información hacia el interior de un contenedor encriptado de grado militar y borra los rastros externos de forma segura.

### **1.3. Experiencia de Uso en Escenario de Crisis**

En el momento del desastre, la experiencia es puramente operativa y libre de fricciones:

1. **Arranque Universal:** El usuario conecta el USB a cualquier ordenador funcional al que tenga acceso (por ejemplo, un portátil de bajo consumo alimentado por un pequeño cargador solar).  
2. **Escritorio Táctico:** Al encender el equipo, entra directamente a un entorno de escritorio ligero y familiar (XFCE), sin necesidad de crear cuentas, iniciar servicios ni conectarse a internet.1  
3. **Acceso Inmediato:** El escritorio está preconfigurado con iconos directos gigantes.  
   * Al hacer clic en **"Enciclopedia Médica"**, se abre el artículo deseado instantáneamente.  
   * Al abrir **"Mapas"**, el usuario puede trazar rutas peatonales o en coche hacia fuentes de agua u hospitales, utilizando el chip GPS del equipo o búsqueda manual sin emitir señales de red.  
   * Al abrir **"IA Local"**, se despliega un chat idéntico a ChatGPT. El usuario puede preguntarle cómo sintetizar penicilina o reparar un motor con las piezas que tiene delante, y la IA razonará la respuesta utilizando exclusivamente el procesador (CPU) de ese ordenador viejo.  
   * Al hacer clic en **"Mis Documentos (Bloqueado)"**, el sistema pide la contraseña maestra y, de repente, materializa una carpeta con todos sus documentos personales vitales, lista para ser consultada de forma segura.

## ---

**2\. El Desafío y Justificación de la Arquitectura**

En un escenario de interrupción prolongada de las telecomunicaciones y la red eléctrica (apagón global, desastres naturales severos), el acceso a la información crítica para la supervivencia humana desaparece.  
Durante la fase de diseño, se evaluaron soluciones existentes como **Project N.O.M.A.D.**, **Internet-in-a-Box (IIAB)** y dispositivos comerciales como **Prepper Disk**. Todas fueron **descartadas** por los siguientes motivos arquitectónicos:

* **Dependencia del Anfitrión (Project N.O.M.A.D.):** Requiere instalarse sobre un sistema operativo Ubuntu/Debian ya existente y funcional, y se basa en la orquestación de contenedores Docker.3 Esto exige un hardware de alto rendimiento y hace imposible su uso como un USB "enchufar y listo" en un ordenador cualquiera.  
* **Dependencia de Hardware Específico (IIAB / Prepper Disk):** Están diseñados primordialmente para operar sobre microordenadores Raspberry Pi como enrutadores Wi-Fi, careciendo de la flexibilidad de un pendrive universal para arquitecturas PC (x86\_64).5

**La Solución Definitiva:** El proyecto "refugiOS" construirá un script automatizado que transformará un USB de alta velocidad en un ecosistema robusto (ya sea mediante un **Live Linux con persistencia nativa** o una **Instalación Completa**), capaz de arrancar en cualquier PC. Descargará binarios portátiles, conocimiento estático e inteligencia artificial local, orquestando bóvedas cifradas para datos personales, sin depender de Docker ni de configuraciones complejas en el ordenador de rescate.

## **3\. Sistema Operativo Base e Internacionalización (i18n)**

El entorno base debe ser extremadamente ligero para maximizar la autonomía de la batería en portátiles alimentados por energía solar.

* **Distribución Base:** **Xubuntu 24.04 LTS** (o distribuciones minimalistas como **Xubuntu 25.10 Minimal**). El entorno de escritorio XFCE consume menos de 1 GB de RAM, reservando los recursos críticos para la Inteligencia Artificial y la renderización de mapas. Las versiones "Minimal" son especialmente valiosas porque eliminan software redundante, liberando espacio clave en el pendrive para datos de supervivencia.  
* **Soporte de Internacionalización (i18n):** El instalador automatizado preguntará al usuario su idioma preferido. Ubuntu permite instalar paquetes de idioma completos desde la línea de comandos sin interacción gráfica utilizando herramientas nativas. El script ejecutará dinámicamente sudo apt install $(check-language-support \-l \<CÓDIGO\_IDIOMA\>) (por ejemplo, es para español o fr para francés), asegurando que el teclado, los menús y las aplicaciones adopten el idioma local del usuario.

## **4\. Módulos de Software Principal y Conocimiento**

El script principal descargará software y bases de datos en función de la capacidad detectada en el disco y las preferencias de idioma del usuario. **Nota de Arquitectura:** Dado que la Fundación Kiwix y otros proyectos publican nuevas versiones de sus archivos añadiendo la fecha al nombre del archivo (ej. \_2026-02.zim), nuestros scripts nunca apuntarán a URLs estáticas. En su lugar, el código utilizará utilidades de terminal (curl, grep, jq) para rastrear dinámicamente la API de GitHub y los repositorios FTP de Kiwix, extrayendo siempre el enlace a la última versión disponible en el momento de la instalación.7

### **4.1. Base de Conocimiento Estática (Kiwix)**

* **Software:** Binario portátil de escritorio Kiwix (formato AppImage). Multilingüe por defecto.  
* **Datos (Archivos ZIM):** Formato de alta compresión. El script seleccionará la URL de descarga del idioma pertinente basándose en el catálogo de la fundación Kiwix.  
  * *Wikipedia Máxima:* Incluye imágenes. (Ej. wikipedia\_es\_all\_maxi para español, \~40-60 GB; la versión en inglés de 2026 ronda los 115 GB).  
  * *WikiMed:* Base de datos médica de emergencia con más de 75.000 artículos (\~2 GB, disponible en múltiples idiomas).10  
  * *WikiHow:* Guías de reparación y supervivencia empírica (wikihow\_es\_maxi, \~25 GB).  
  * *Survivor Library:* Documentación histórica en inglés para reconstrucción de tecnología preindustrial, agricultura y metalurgia (\~250 GB).9

### **4.2. Navegación Topográfica y Mapas (Organic Maps)**

* **Software:** **Organic Maps** para Linux Desktop. Es una aplicación de código abierto enfocada en la privacidad, que no requiere conexión a internet para el cálculo de rutas ni búsquedas.12  
* **Internacionalización:** Soporta más de 30 idiomas nativamente (incluyendo árabe, chino, español, francés, etc.).  
* **Datos:** Basado en OpenStreetMap. El script descargará los datos vectoriales (países o continentes enteros) al directorio de la aplicación, permitiendo mapas extremadamente detallados (fuentes de agua, senderos) en pocos gigabytes.

### **4.3. Inteligencia Artificial como Asistente Activo (Llamafile)**

* **Software:** Prescindimos de instalaciones de Python y Docker. Usaremos **Llamafile**, que compila el motor de inferencia (llama.cpp) y el modelo en un único archivo ejecutable (.exe/.sh).13  
* **Modelos de Lenguaje Pequeños (SLM):** Optimizados para ejecutarse únicamente con la CPU del ordenador anfitrión y un mínimo de 4 GB a 8 GB de RAM.15  
  * *Microsoft Phi-3.5 Mini (3.8B):* Destaca por su capacidad para procesar ventanas de contexto inmensas (hasta 128K tokens), ideal para ingerir manuales locales enteros y responder preguntas sobre ellos. Soporta razonamiento nativo en 23 idiomas.17  
  * *DeepSeek R1 / Qwen (1.5B):* Especializado en cadenas de pensamiento matemático y lógico para equipos de hardware muy obsoleto.18

## **5\. Ofimática, Multimedia y Paquetes Temáticos Opcionales**

Un dispositivo de supervivencia necesita herramientas para manipular los datos personales, leer planos y abrir archivos recuperados. Al estar en un entorno Ubuntu completo, el script install.sh aprovechará el gestor apt para preinstalar paquetería estándar del repositorio oficial, garantizando que el usuario no dependa de internet en el futuro.

* **Paquete Ofimático Básico (Por Defecto):**  
  * libreoffice-writer, libreoffice-calc, libreoffice-impress (Visualización de documentos, hojas de cálculo de inventario).  
  * *Internacionalización:* Se instalará el paquete libreoffice-l10n-\<IDIOMA\> correspondiente.  
  * evince o atril (Visualización rápida de planos y PDF).  
  * vlc (Reproductor multimedia universal sin dependencia de códecs externos).  
  * ristretto o eog (Visor de imágenes ligero).  
* **Paquetes Temáticos (Seleccionables por el usuario en base a la capacidad):**  
  * *Pack Desarrollo/Ingeniería:* build-essential, python3, git, vim, nano, simuladores de circuitos (ej. kicad o ngspice si el espacio lo permite).  
  * *Pack Educación:* gcompris (suite educativa para niños), scratch (programación básica offline).

## **6\. Bóvedas Criptográficas Personales Dinámicas (LUKS)**

El sistema de protección de datos personales (pasaportes, contratos, historiales médicos) requiere un encapsulamiento criptográfico. Si la arquitectura elegida es un *Live USB*, la partición entera no puede cifrarse, por lo que se crearán **contenedores de archivos de imagen**.

* **Tecnología Subyacente:** cryptsetup luksFormat, montaje en dispositivos de bucle (loop devices) y formato interno ext4.  
* **Ventajas:** Permite tener múltiples bóvedas independientes en el escritorio (ej. una médica, una financiera) con diferentes contraseñas.  
* **Mecánica de Inyección:** El usuario conecta su USB habitual de Windows/Mac con sus documentos. Ejecuta el script de creación. El script mide el tamaño de la carpeta, genera un archivo .img de un tamaño ligeramente superior en el USB de supervivencia, lo formatea con LUKS, pide una contraseña maestra al usuario, transfiere los archivos internamente con rsync y sella la bóveda.

*(Nota: Si el usuario opta por la "Instalación Completa" explicada en la sección 8, el cifrado de disco completo LUKS estará integrado a nivel de sistema, aunque estas bóvedas por archivo siguen siendo útiles para la portabilidad cruzada o la negabilidad plausible).*

## **7\. Organización del Repositorio de Desarrollo (GitHub)**

El repositorio debe estar altamente compartimentado para que el equipo de desarrollo pueda trabajar en paralelo.

### **Estructura de Directorios**

refugiOS/  
├── README.md \<-- Instrucciones de uso e inicialización.  
├── install.sh \<-- Entrypoint ("One-Liner" a ejecutar en la terminal).  
├── scripts/  
│ ├── 01\_system\_check.sh \<-- Detecta el espacio (df \-B1) y actualiza apt.  
│ ├── 02\_i18n\_setup.sh \<-- Instala language-packs de Ubuntu para el sistema.  
│ ├── 03\_ui\_menu.sh \<-- Interfaz TUI (whiptail/zenity) para seleccionar paquetes.  
│ ├── 04\_downloader.sh \<-- Lógica de descarga robusta de ZIMs, IA y AppImages.  
│ ├── 05\_apt\_packages.sh \<-- Instalación de LibreOffice, VLC y paquetes temáticos.  
│ ├── 06\_desktop\_setup.sh \<-- Crea accesos directos (.desktop) en el escritorio XFCE.  
│ └── 07\_vault\_manager.sh \<-- Lógica de las bóvedas LUKS (Crear, Abrir, Cerrar).  
└── assets/  
├── icons/ \<-- Iconos SVG/PNG para las bóvedas y los programas.  
└── desktop\_templates/ \<-- Plantillas de los ficheros.desktop.

### **Funcionalidad de los Scripts Clave**

* **El "One-Liner" (install.sh):**  
  El usuario abrirá una terminal en su recién iniciado Xubuntu y pegará:  
  curl \-fsSL https://raw.githubusercontent.com/usuario/refugios/main/install.sh | bash  
  Este script descargará el resto del repositorio a /tmp/refugios y delegará la ejecución al resto de módulos secuencialmente.  
* **Encuesta y Detección (01\_system\_check.sh y 03\_ui\_menu.sh):**  
  Detectará si existe conexión a internet, validará el espacio libre exacto y lanzará una interfaz por terminal. Preguntará: *Idioma deseado*, *Tamaño de Wikipedia (Mini/Maxi)*, y qué *Paquetes Temáticos* (Educación, Ingeniería) se desean instalar.  
* **Gestor del Escritorio (06\_desktop\_setup.sh):**  
  Eliminará elementos innecesarios del escritorio por defecto de Ubuntu. Escribirá ficheros .desktop que actúen como lanzadores directos.  
  *Ejemplo:* El icono "Manual de Supervivencia" ejecutará transparentemente el comando /opt/refugiOS/kiwix.appimage /opt/refugiOS/data/survivor\_library.zim, abriendo el conocimiento instantáneamente.  
* **Gestor de Bóvedas Criptográficas (07\_vault\_manager.sh):**  
  Instalará tres alias en el sistema accesibles mediante iconos en el escritorio:  
  1. **"Nueva Bóveda":** Usa dd para crear un bloque, pide clave con un pop-up gráfico, aplica cryptsetup luksFormat, formatea a ext4 y copia los datos del usuario.  
  2. **"Desbloquear Bóveda":** Pide la clave maestra gráficamente, ejecuta cryptsetup luksOpen y monta el archivo .img en una carpeta en el Escritorio.  
  3. **"Bloquear Bóveda":** Aplica umount y cryptsetup luksClose, desapareciendo la carpeta del escritorio para garantizar la seguridad inmediata.

## ---

**8\. Guía Técnica de Ensamblaje Manual (Prueba de Concepto)**

Antes de programar la automatización, es imperativo construir un "refugiOS" a mano para validar la viabilidad de todos los subsistemas. Los siguientes pasos detallan cómo crear el entorno operativo completo, asumiendo un nivel técnico intermedio en entornos Linux (como Debian).

### **8.1. Selección de la Imagen ISO Base**

La base tecnológica será Xubuntu. Puedes usar **Xubuntu 24.04 LTS Minimal** o **Xubuntu 25.10 Minimal**. Las versiones "Minimal" (archivos de \~1.5 GB a 2 GB frente a los \~3.5 GB estándar) son idóneas; carecen de juegos y software secundario preinstalado, lo que maximiza la porción de disco disponible para persistencia de datos vitales.

### **8.2. Estrategias de Capacidad según tu Pendrive**

Antes de empezar a descargar, debes planificar qué recursos vas a integrar según el tamaño físico de tu pendrive:

* **16 GB (Mínimo Absoluto \- Modo Supervivencia Extrema):**  
  * Espacio muy crítico. Solo podrás instalar: El sistema operativo base (\~2 GB), la enciclopedia médica *WikiMed* (\~2 GB), mapas de tu región local con *Organic Maps* (\~1 GB), un modelo de IA de razonamiento ultraligero como *DeepSeek R1 1.5B* (\~1.1 GB), y te sobrará espacio para una pequeña Bóveda LUKS de 1 o 2 GB para pasaportes. *La Wikipedia general queda totalmente excluida.*  
* **32 GB (Modo Táctico Ligero):**  
  * Instala lo del bloque anterior, pero puedes añadir una versión de la Wikipedia de tamaño reducido, por ejemplo, wikipedia\_es\_all\_nopic (sin imágenes) o una versión "Mini" (solo introducciones). También puedes incluir una Bóveda de datos personales más grande (hasta 5 GB).  
* **64 GB (Tu pendrive actual \- Modo Estándar):**  
  * Esta es la capacidad ideal para tener una herramienta equilibrada. Tendrás espacio de sobra para: Xubuntu Minimal, la **Wikipedia en Español Maxi completa con imágenes** (\~40 GB a 45 GB dependiendo de la fecha de volcado), WikiMed (2 GB), mapas de toda Europa o Norteamérica (5-10 GB), el sofisticado modelo *Phi-3.5 Mini* (2.4 GB), y una Bóveda personal holgada (5 GB).  
* **128 GB o más (La Biblioteca de Alejandría):**  
  * Aquí desaparecen las restricciones. Podrías incluir la Wikipedia maestra en Inglés con imágenes (que excede los 115 GB), o añadir la vasta biblioteca *Survivor Library* de tecnología preindustrial (\~250 GB) si utilizas un disco SSD de 512 GB.

### **8.3. Paradigma de Despliegue: Live USB vs. Instalación Completa**

Antes de grabar el sistema, el operador debe decidir la arquitectura subyacente. Existen dos enfoques técnicos diametralmente opuestos para ejecutar Linux desde un dispositivo extraíble:  
**Opción A: Entorno Live con Persistencia (El enfoque más portátil y amigable)**  
El sistema arranca desde una imagen ISO comprimida de solo lectura (alojada en el pendrive) y guarda tus configuraciones en una partición secundaria (casper-rw o writable).

* **Ventajas:** Minimiza drásticamente los ciclos de escritura-borrado en la memoria NAND, prolongando la vida útil de los pendrives estándar. Además, es un método seguro de fabricar, sin riesgo de dañar la máquina anfitriona.  
* **Desventajas:** El tiempo de arranque inicial es notablemente más lento debido a la descompresión al vuelo hacia la memoria RAM y a la propia tecnología del USB.

**Opción B: Instalación Completa o "Full Install" (El enfoque de máximo rendimiento)**  
Consiste en instalar el sistema operativo de forma nativa en el USB, procesándose exactamente igual que si fuera el disco duro interno de un PC.

* **Ventajas:** Tiempos de arranque fulgurantes, rendimiento nativo fluido y la posibilidad de aplicar cifrado de disco completo (LUKS) directamente desde el instalador de Ubuntu.  
* **Desventajas:** Exige ineludiblemente el uso de un SSD portátil de alta velocidad (las memorias USB baratas morirán prematuramente por el estrés de lectura/escritura constante de un OS nativo). **Requiere extrema precaución al crearlo:** El instalador de Ubuntu tiende a sobreescribir el gestor de arranque (GRUB) de la máquina anfitriona de forma involuntaria. Es obligatorio desconectar físicamente los discos internos antes de la instalación.

### ---

**8.4. Creación del Medio Físico: Vía Live-USB con Persistencia**

Si has optado por la Opción A (seguridad y pendrives estándar). En Ubuntu 20.04 y superior (incluyendo 24.04/25.10), la partición de persistencia debe estar formateada en ext4 y tener la etiqueta exacta de volumen **writable**.  
**Método A.1: Usando mkusb en Debian (Recomendado y Seguro)**  
Dado que estás en Debian y mkusb es una herramienta de los repositorios PPA de Ubuntu, debes añadir el repositorio. Para hacerlo fácilmente desde la terminal:

Bash

\# 1\. Instalar el gestor de claves y añadir la clave GPG  
sudo apt install dirmngr  
sudo apt-key adv \--keyserver keyserver.ubuntu.com \--recv 54B8C8AC

\# 2\. Añadir el repositorio PPA de Ubuntu (focal) a Debian  
echo "deb http://ppa.launchpad.net/mkusb/ppa/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/mkusb.list

\# 3\. Actualizar e instalar mkusb  
sudo apt update  
sudo apt install mkusb usb-pack-efi

Una vez instalado, ejecuta mkusb desde la terminal o el menú de aplicaciones, selecciona "Install (make a boot device)" \-\> "Persistent live \- only Debian and Ubuntu", elige tu ISO de Xubuntu Minimal, selecciona tu pendrive y asigna el 100% del espacio restante a la partición de persistencia.  
**Método A.2: Puramente Manual desde la Terminal (Nivel Experto)**  
Si prefieres no añadir repositorios, puedes crear la persistencia a mano utilizando dd y fdisk:

1. Identifica tu unidad USB (ej. /dev/sdX \- ¡asegúrate de que sea la correcta usando lsblk\!).  
2. Graba la imagen ISO (esto destruirá todos los datos del pendrive):  
   Bash  
   sudo dd if=xubuntu-25.10-minimal-amd64.iso of=/dev/sdX bs=4M status=progress

3. Arregla la tabla de particiones y crea la partición de persistencia en el espacio libre restante:  
   Bash  
   sudo fdisk /dev/sdX  
   \# Dentro de fdisk, presiona las siguientes teclas:  
   \# n (nueva partición) \-\> p (primaria) \-\> 3 (número de partición)  
   \# \[Enter\] (primer sector por defecto) \-\> \[Enter\] (todo el espacio restante)  
   \# w (escribir cambios y salir)

4. Formatea la nueva partición con la etiqueta obligatoria writable:  
   Bash  
   sudo mkfs.ext4 \-L writable /dev/sdX3

### ---

**8.5. Creación del Medio Físico: Vía Instalación Completa (Full Install)**

Si has optado por la Opción B (máximo rendimiento y cuentas con un disco externo tipo SSD-USB).

1. **Preparación del Instalador Temporero:** Utiliza un USB secundario pequeño (ej. 8 GB) para "quemar" la ISO de Xubuntu Minimal de forma normal usando Rufus, balenaEtcher o dd.  
2. **Aislamiento Físico (Paso Crítico):** Apaga tu ordenador de trabajo, ábrelo y **desconecta físicamente el cable SATA o extrae el disco NVMe interno** de tu PC. Si omites este paso, al realizar la instalación, el sistema insertará el gestor de arranque en tu disco de Windows/Debian, arruinando su capacidad de arranque.  
3. **Proceso de Instalación:**  
   * Inserta tanto el USB "Instalador" como el "USB Destino" (el SSD para *refugiOS*).  
   * Arranca el ordenador desde el USB Instalador.  
   * Inicia el asistente de instalación de Xubuntu.  
   * Al llegar a la sección de particionado, selecciona "Borrar disco e instalar Ubuntu" asegurándote de elegir en el desplegable inferior tu unidad USB Destino.  
   * Opcional (Máxima seguridad): Aquí puedes pulsar en "Características Avanzadas" y seleccionar **LVM con cifrado LUKS** para que el disco entero nazca cifrado de fábrica.  
   * Procede con la instalación. El sistema instalará los directorios raíz (/) y la partición EFI directamente en el dispositivo extraíble.  
4. **Finalización:** Una vez completada la instalación, apaga el equipo, retira el USB instalador, vuelve a conectar tu disco duro interno de la máquina y enciéndela. Ya posees un ordenador de bolsillo ultrarrápido y nativo.

*(A partir de este punto, ya uses la Opción A o la Opción B, el entorno está listo. Los siguientes pasos de configuración se ejecutan arrancando desde tu nuevo sistema "refugiOS").*

### ---

**8.6. Arranque y Preparación del Entorno Base**

**¡IMPORTANTE PARA USUARIOS DEL MÉTODO LIVE USB MANUAL (Opción A.2)\!**  
El gestor de arranque GRUB incluido en la imagen ISO estándar no está configurado para montar tu nueva partición gigante automáticamente; si lo dejas arrancar por defecto, se cargará todo en la memoria RAM y te quedarás sin espacio en unos pocos minutos (la partición / se llenará). Para evitarlo y activar tu partición writable:

1. En el menú de arranque negro (GRUB), selecciona la opción "Try Xubuntu" pero **NO presiones Enter**. Presiona la tecla **e**.  
2. Busca la línea que empieza por la palabra linux (suele terminar en quiet splash \---).  
3. Añade la palabra persistent al final de esa línea, quedando algo como: ... quiet splash persistent \---.  
4. Pulsa Ctrl+X o F10 para arrancar. *(Nota: En nuestra futura versión final con scripts, editaremos el archivo grub.cfg del USB para inyectar esta palabra permanentemente).*

Una vez dentro del escritorio (puedes comprobar que tienes todo el espacio disponible escribiendo df \-h / en la terminal), instala las dependencias y crea las carpetas base:

Bash

sudo apt update  
sudo apt install cryptsetup curl wget aria2 jq flatpak rsync libreoffice vlc evince \-y  
sudo apt install $(check-language-support \-l es) \-y  
mkdir \-p \~/refugiOS/{Apps,Conocimiento,Mapas,IA,Bovedas,Scripts}

### **8.7. Validación mediante Máquina Virtual (Testeo sin reiniciar)**

Para agilizar enormemente el proceso de ensamblaje y prueba de los pasos anteriores (especialmente si usas el modo Live USB), puedes arrancar el pendrive físico directamente dentro de una máquina virtual (VM) en tu sistema anfitrión.  
**Importante sobre el modo de arranque:** Por defecto, QEMU intenta arrancar usando una BIOS antigua (Legacy/SeaBIOS). Las imágenes modernas de Linux (y las instalaciones nativas completas) están diseñadas y optimizadas para sistemas UEFI. Si arrancas sin especificar el firmware UEFI, te encontrarás con un error de GRUB (como unknown filesystem o grub rescue\>). Por ello, es imperativo instalar el firmware OVMF y pasarle a QEMU el parámetro \-bios para forzar el arranque nativo en modo UEFI.  
**1\. Identifica tu dispositivo USB:**  
Asegúrate de conocer su identificador ejecutando lsblk en la terminal (asumiremos que es /dev/sdc para estos ejemplos). Asegúrate de que las particiones no estén montadas en tu sistema anfitrión.  
**2\. Instalación y Ejecución en modo UEFI (OVMF) según tu Distribución:**

* **Para sistemas tipo Debian (Debian, Ubuntu, Linux Mint):**  
  Bash  
  sudo apt update && sudo apt install qemu-system-x86 qemu-kvm ovmf  
  sudo qemu-system-x86\_64 \-enable-kvm \-m 4096 \-bios /usr/share/ovmf/OVMF.fd \-drive file=/dev/sdc,format=raw

* **Para sistemas tipo Red Hat (Fedora, RHEL, CentOS):**  
  Bash  
  sudo dnf install qemu-kvm edk2-ovmf  
  sudo qemu-kvm \-m 4096 \-bios /usr/share/edk2/ovmf/OVMF\_CODE.fd \-drive file=/dev/sdc,format=raw

* **Para sistemas Arch Linux (Manjaro, EndeavourOS):**  
  Bash  
  sudo pacman \-S qemu-desktop edk2-ovmf  
  sudo qemu-system-x86\_64 \-enable-kvm \-m 4096 \-bios /usr/share/edk2-ovmf/x64/OVMF\_CODE.fd \-drive file=/dev/sdc,format=raw

**3\. Resolución de problemas frecuentes (Tips de Precaución):**

* **Error "Could not access KVM kernel module":** Significa que la virtualización por hardware está apagada a nivel físico. Debes reiniciar tu ordenador una vez, entrar en la BIOS/UEFI y buscar opciones como **"SVM Mode" (en procesadores AMD)** o **"Intel VT-x"** y activarla. Tras esto, QEMU funcionará perfectamente.  
* **Peligro al asignar la unidad (/dev/sda):** En equipos tradicionales, /dev/sda suele ser el **disco duro principal del ordenador anfitrión**. Si ordenas a QEMU arrancar una máquina virtual sobre el disco duro que estás usando activamente, corromperás tus datos de forma irremediable. Verifica siempre con lsblk.  
* **Advertencias de Formato:** Nunca uses el atajo \-hda para discos físicos bajo QEMU. Debes usar la estructura explícita \-drive file=/dev/sdX,format=raw para indicar que el bloque es en bruto.

#### **Obras citadas**

1. I'm building a plug-and-play USB drive that gives you offline AI, maps, Wikipedia, and survival guides — no internet needed, ever. \- Reddit, fecha de acceso: marzo 23, 2026, [https://www.reddit.com/r/prepping/comments/1rjopiu/im\_building\_a\_plugandplay\_usb\_drive\_that\_gives/](https://www.reddit.com/r/prepping/comments/1rjopiu/im_building_a_plugandplay_usb_drive_that_gives/)  
2. I'm building a plug-and-play USB drive with offline maps, AI, Wikipedia, and survival guides \- a portable knowledge library for when you're truly off the grid. \- Reddit, fecha de acceso: marzo 23, 2026, [https://www.reddit.com/r/OffGrid/comments/1rkuvl0/im\_building\_a\_plugandplay\_usb\_drive\_with\_offline/](https://www.reddit.com/r/OffGrid/comments/1rkuvl0/im_building_a_plugandplay_usb_drive_with_offline/)  
3. GitHub \- Crosstalk-Solutions/project-nomad, fecha de acceso: marzo 23, 2026, [https://github.com/Crosstalk-Solutions/project-nomad](https://github.com/Crosstalk-Solutions/project-nomad)  
4. Project NOMAD \- Offline Knowledge & AI Server, fecha de acceso: marzo 23, 2026, [https://www.projectnomad.us/](https://www.projectnomad.us/)  
5. The Internet in a Box Project \- disruptively-useful \- Obsidian Publish, fecha de acceso: marzo 23, 2026, [https://publish.obsidian.md/disruptively-useful/The+Heat+Strikes/Civil+Resistance/Case+Studies/The+Internet+in+a+Box+Project](https://publish.obsidian.md/disruptively-useful/The+Heat+Strikes/Civil+Resistance/Case+Studies/The+Internet+in+a+Box+Project)  
6. Do You Need PrepperDisk, the Off-The-Grid Raspberry Pi-Powered Reference Library?, fecha de acceso: marzo 23, 2026, [https://lowendbox.com/blog/do-you-need-prepperdisk-the-off-the-grid-raspberry-pi-powered-reference-library/](https://lowendbox.com/blog/do-you-need-prepperdisk-the-off-the-grid-raspberry-pi-powered-reference-library/)  
7. Internet in a Box \- Mandela's Library of Alexandria, fecha de acceso: marzo 23, 2026, [https://internet-in-a-box.org/](https://internet-in-a-box.org/)  
8. Prepper disk? : r/TwoXPreppers \- Reddit, fecha de acceso: marzo 23, 2026, [https://www.reddit.com/r/TwoXPreppers/comments/1i61g9k/prepper\_disk/](https://www.reddit.com/r/TwoXPreppers/comments/1i61g9k/prepper_disk/)  
9. Has your post-apocalyptic prep kit got a spare 250GB? Check out the new Survivor Library ZIM\! Could save your bacon (literally)\! : r/Kiwix \- Reddit, fecha de acceso: marzo 23, 2026, [https://www.reddit.com/r/Kiwix/comments/1fl53xm/has\_your\_postapocalyptic\_prep\_kit\_got\_a\_spare/](https://www.reddit.com/r/Kiwix/comments/1fl53xm/has_your_postapocalyptic_prep_kit_got_a_spare/)  
10. WikiMed by Kiwix \- Free download and install on Windows | Microsoft Store, fecha de acceso: marzo 23, 2026, [https://apps.microsoft.com/detail/9phjsnp1cz8j?hl=en-US\&gl=US](https://apps.microsoft.com/detail/9phjsnp1cz8j?hl=en-US&gl=US)  
11. Survivor Library, fecha de acceso: marzo 23, 2026, [https://www.survivorlibrary.com/](https://www.survivorlibrary.com/)  
12. Organic Maps: Offline Hike, Bike, Trails and Navigation, fecha de acceso: marzo 23, 2026, [https://organicmaps.app/](https://organicmaps.app/)  
13. Running LLaMA 3.2 Locally with Llamafile: A Hands-On Guide | by Prakash | Medium, fecha de acceso: marzo 23, 2026, [https://medium.com/@rprak9047/running-llama-3-2-locally-with-llamafile-a-hands-on-guide-76e717d0124e](https://medium.com/@rprak9047/running-llama-3-2-locally-with-llamafile-a-hands-on-guide-76e717d0124e)  
14. Why is llamafile seemingly slower than ollama on my system for the same model and same query ? \#614 \- GitHub, fecha de acceso: marzo 23, 2026, [https://github.com/Mozilla-Ocho/llamafile/discussions/614](https://github.com/Mozilla-Ocho/llamafile/discussions/614)  
15. The Best Open-Source Small Language Models (SLMs) in 2026 \- BentoML, fecha de acceso: marzo 23, 2026, [https://www.bentoml.com/blog/the-best-open-source-small-language-models](https://www.bentoml.com/blog/the-best-open-source-small-language-models)  
16. Top 7 Small Language Models You Can Run on a Laptop \- MachineLearningMastery.com, fecha de acceso: marzo 23, 2026, [https://machinelearningmastery.com/top-7-small-language-models-you-can-run-on-a-laptop/](https://machinelearningmastery.com/top-7-small-language-models-you-can-run-on-a-laptop/)  
17. Best Small Language Models (March 2026): Run AI on 4GB RAM — Phi-4, Gemma 3, Qwen 3 | Local AI Master, fecha de acceso: marzo 23, 2026, [https://localaimaster.com/blog/small-language-models-guide-2026](https://localaimaster.com/blog/small-language-models-guide-2026)  
18. Top 5 Best LLM Models to Run Locally in CPU (2025 Edition) \- Kolosal AI, fecha de acceso: marzo 23, 2026, [https://www.kolosal.ai/blog-detail/top-5-best-llm-models-to-run-locally-in-cpu-2025-edition](https://www.kolosal.ai/blog-detail/top-5-best-llm-models-to-run-locally-in-cpu-2025-edition)