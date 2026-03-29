# Visión General y Experiencia del Usuario

El presente documento constituye la hoja de ruta técnica y arquitectónica en lo que respecta a la misión funcional del proyecto. Para garantizar que las decisiones de ingeniería estén alineadas con el producto final, a continuación se define el comportamiento de **refugiOS** desde la perspectiva del usuario final.

## 1. Propósito, Casos de Uso y Nomenclatura

El nombre **refugiOS** nace de la fusión conceptual entre la palabra "Refugio" y el acrónimo informático "OS" (Sistema Operativo). A diferencia de términos como "navaja suiza", que pueden evocar un uso táctico agresivo o utilitario, la palabra *refugio* transmite la verdadera esencia del proyecto: un santuario o búnker digital seguro, inexpugnable e inalterable, destinado a salvaguardar el conocimiento humano, la identidad personal y la vida frente al colapso de las infraestructuras organizadas.

**refugiOS** está diseñado como una herramienta de extrema supervivencia "plug-and-play" y 100% offline. 

Sus **casos de uso** abarcan:
*   **Desastres Naturales Severos:** Terremotos, huracanes o inundaciones donde las conexiones a Internet pueden estar caídas durante meses.
*   **Apagones Globales (Blackouts):** Colapso prolongado de la red eléctrica o de telecomunicaciones.
*   **Asistencia en Zonas Remotas:** Regiones rurales sin infraestructura moderna.
*   **Protección de la Información:** Herramienta vital para periodistas, disidentes o activistas en entornos hostiles que requieran negar el acceso a su información a través de la criptografía.

Su objetivo último es permitir que el usuario convierta _cualquier_ ordenador de consumo disponible (incluso hardware muy obsoleto rescatado de la basura) en un potente centro de conocimiento, navegación e inteligencia artificial completamente autárquico.

---

## 2. Experiencia de Instalación (La fase del "Preparador")

El proceso de creación del dispositivo debe ser sumamente intuitivo y desatendido, exigiendo conocimientos técnicos mínimos por parte del usuario, priorizando que cualquiera pueda armarlo en la seguridad de su hogar antes del "Día de la Crisis":

1.  **Preparación del Medio Físico:** El usuario adquiere un pendrive USB o disco SSD portátil de alta capacidad y rendimiento. Utilizando su sistema habitual, graba una imagen ISO estándar de Linux (Xubuntu) configurada con persistencia nativa, o bien efectúa una instalación completa sobre ese disco externo.
2.  **Ejecución del Instalador (Entrypoint):** El usuario arranca su ordenador desde ese nuevo disco USB, abre una ventana de terminal y pega un único comando proporcionado por nosotros (el famoso *One-Liner* de instalación).
3.  **Configuración Interactiva:** El script de instalación toma el control total. Lanza un asistente visual a través de menús pop-up o en terminal (TUI) para adaptar el sistema:
    *   *Detección Inteligente:* Verifica el espacio de almacenamiento real del dispositivo.
    *   *Idioma de la Interfaz:* Ofrece ajustar la paquetería, menús y teclados enteros a la selección regional (español, francés, inglés, etc.).
    *   *Módulos de Conocimiento:* Pregunta qué bibliotecas instalar basándose en el espacio (Ej: "¿Wikipedia Completa o sólo texto?", "Manuales médicos", "Biblioteca Agrícola").
    *   *Cartografía Geográfica:* Ofrece descargar las regiones de interés para el GPS.
    *   *Paquetes Especiales:* Permite inyectar herramientas ofimáticas, emuladores o lenguajes de programación.
4.  **Generación de la Bóveda Privada Inicial:** Una vez descargado todo el conocimiento open-source, el asistente transita a la información sensible. Invita al usuario a inyectar en el USB de supervivencia todos sus documentos vitales (pasaportes, historiales médicos, actas notariales, monederos de criptodivisas) en una Bóveda protegida por una clave maestra y cifrado de grado militar.

---

## 3. Experiencia de Uso en Escenario de Crisis

En el momento en que ocurre el desastre, la experiencia debe estar desprovista de toda fricción técnica, barrera de configuración y frustración operativa:

1.  **Arranque Universal:** Al no haber comunicaciones, el usuario toma su USB de refugiOS y lo conecta a cualquier ordenador funcional que encuentre —por ejemplo, un viejo portátil de bajo consumo alimentado por un panel solar portátil—.
2.  **Escritorio Táctico Liviano:** Al encender el equipo, ingresa en segundos y directamente a un entorno de escritorio extremadamente ligero (XFCE). Sin pedir credenciales de internet, sin inicio de servicios redundantes ni conexiones WiFi inútiles.
3.  **Acceso Inmediato (Clic-y-Listo):** El escritorio está limpio y preconfigurado con iconos gigantes inequívocos:
    *   **"Enciclopedia Médica":** Abre instantáneamente artículos sobre la sutura de heridas y reconocimiento de enfermedades.
    *   **"Mapas":** Mediante un clic, se pueden trazar rutas de senderismo precisas hacia cuerpos de agua dulce u hospitales lejanos, utilizando únicamente la base instalada a nivel global, sin emitir ningún rastreo hacia el exterior.
    *   **"Inteligencia Artificial Local":** Se despliega una interfaz idéntica a ChatGPT clásico. El usuario le puede hacer consultas como _"¿Cómo sintetizar penicilina natural?"_ o _"Con este carburador de la marca X, ¿cómo lo reparo?"_, y el sistema inferirá la respuesta utilizando exclusivamente el procesador primitivo de la máquina, apoyándose en la base de datos descargada.
    *   **"Mis Documentos (Bloqueado)":** Clic, un pop-up que requiere nuestra contraseña física y, de repente, se materializa en el escritorio una carpeta efímera con todos nuestros documentos vitales para tramitar ayuda, evacuar áreas o presentar identidades a los cuerpos de seguridad.
