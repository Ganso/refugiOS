# Arquitectura de las Bóvedas Criptográficas (Protección LUKS)

La vida en zonas conflictivas o durante una avalancha y traslado temporal masivo, implica un alto nivel de asaltos o confiscaciones por parte de retenes autoritarios y/o saqueos ante la necesidad de recursos primarios.

Exponer de forma llana actas notariales, identificadores DNI, pasaportes internacionales, carteras con claves seed para criptomonedas o información médica fundamental en un pendrive tirado en una mochila, significa una muerte financiera e identitaria.

refugiOS se diseña asumiendo como certeza absoluta que la unidad física flash va a ser hurtada u obligada a ser encendida. Para lidiar con este eventual robo, todos los subsistemas personales deben residir sellados herméticamente.

## Metodología del Cifrado a Nivel de Archivo Dinámico (Bóvedas por Loop)

Si el operador armó una Instalación Completa (Full OS), el asistente de Ubuntu inicializa un disco duro nativo usando encriptación FDE (Full Disk Encryption, todo cifrado).
Sin embargo, esta solución se complica bajo el uso de un Sistema "Live USB con persistencia extendida", en cuyo caso particionar masivamente toda la NAND genera un desgaste irrecuperable con el tiempo y reduce drásticamente las bondades pasivas portátiles en estaciones secundarias ajenas en la terminal (dificultando las descargas).

Para solventar esta debilidad de la modularidad extraíble, refugiOS implementa un emulador Criptográfico Virtual basado en **Bóvedas de Imagen**.

### El Substrato de los Contenedores.
*   **El Proceso de Inyección:** Durante el montaje, en lugar de encriptar el hardware, el usuario conecta su PC normal mediante un disco con su carpeta "TODA MI VIDA.pdf". El `install.sh` se interviene, ejecutando comandos de metraje que determinan y examinan milimétricamente el directorio (`du -sh`), multiplicando el espacio un 10-15% en favor del aire, y utilizando la suite Unix de bloque (`dd` byte a byte) instanciando un archivo muerto inerte en `/home/refugiOS/boveda_A.img`.
*   Atañe el núcleo del instalador usar el gestor del Kernel FOSS: `cryptsetup luksFormat` y forja bajo grado militar para asignarle una capa transparente sobre su cabecera. Convierte su extensión pasiva y mediante la clave del usuario (requerido al vuelo por interfaz prompt emergente Zenity) instanciando la imagen `loop-device`, pre formatea a la norma Ext4, emula el copiado rsync estricto desde sus documentos a un sub-anfitrión y finaliza rompiendo el eslabón, desmontándolo de vuelta a una amalgama negra codificada aleatoriamente en el escritorio.

## Funcionalidad Dinámica y Modularidad del Escritorio Táctico

Dado que el objetivo prioritario reside en apartar del estrés al usuario en estado de crisis total: El gestor de bóvedas (`07_vault_manager.sh`) inyecta atajos visuales gigantes `.desktop` como botones interactivos que camuflan llamadas potentes a la terminal bajo el capó de la acción visual:
1.  **"Nueva Bóveda Mágica":** Aparece una ventana al darle doble click: _"Dime el tamaño libre que otorgaré y qué contraseña vas a establecer"_. Y se instancia una segunda variante (.IMG), operando un contenedor "Médico", otro "Financiero" permitiendo distintas capas lógicas (y diversas mentiras pasibles).
2.  **"Desbloquear Bóveda":** Al presionar click, una bonita barra GUI salta ordenando teclear la clave maestra de apertura. Invoca `luksOpen` asignando y materializando la carpeta "Archivos" virtual en el escritorio XFCE para ver, transaccionar e imprimir las escrituras del usuario. 
3.  **"Bloquear Bóveda":** Con pulsar en este "Cerrado rápido temporal", el script ataja instanciando `umount` estricto a las raíces persistentes, llamando con `luksClose` como cerrojo seguro y desintegrando la carpeta montada del entorno visual para desaparecer mágicamente del SO en nanosegundos ante la aproximación de un desconocido en la habitación.
