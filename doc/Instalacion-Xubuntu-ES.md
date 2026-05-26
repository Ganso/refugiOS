# Guía de Instalación en XUbuntu

Esta guía explica en detalle cómo preparar tu unidad de refugiOS sobre una base de **XUbuntu** desde cualquier sistema operativo (Windows o Linux).

> [!IMPORTANT]
> **Antes de empezar:** La elección del dispositivo físico (pendrive, SSD, adaptador) y su capacidad condicionan el rendimiento y los contenidos que podrás instalar. Consulta la **[Guía de Elección del Medio de Instalación](Eleccion-Medio-Instalacion-ES.md)** para tomar la mejor decisión según tu presupuesto.

---

## 1. Descarga de la imagen base (El software)

Utilizamos versiones ligeras de Xubuntu para maximizar el espacio libre disponible:

*   [**Xubuntu 24.04 LTS (Recomendado)**](https://xubuntu.org/): La opción más estable con soporte garantizado durante años.
*   [**Xubuntu 25.10 (Última versión)**](https://xubuntu.org/): Si prefieres tener kernels más modernos para hardware muy nuevo, aunque con un ciclo de soporte más corto.
*   **Aviso:** Descarga siempre la variante **"Minimal"** para ahorrar unos 2 GB de espacio eliminando programas innecesarios (juegos, ofimática pesada, etc.).

---

## 2. Creación de la unidad de arranque

Hay dos formas principales de configurar el sistema. Lee con atención:

### Opción A: USB "Live" con Persistencia (Recomendado)
El sistema reside de forma segura en una imagen inerte (SquashFS) y los cambios se guardan en la partición `writable`. Esto evita el desgaste excesivo de la memoria y protege tu ordenador anfitrión.

*   **Desde Windows:** Usa [**Rufus**](https://rufus.ie/). Al elegir la ISO, arrastra el deslizador de **"Tamaño de partición persistente"** al máximo posible (dejando un poco de aire).
*   **Desde Ubuntu:**
    Tienes dos formas principales de preparar el USB:
    1.  **Opción 1: [Creador de discos de arranque (Guía oficial)](https://help.ubuntu.com/stable/ubuntu-help/addremove-creator.html.es)**. Es la herramienta nativa y más sencilla si no necesitas persistencia avanzada.
    2.  **Opción 2: mkusb (Usuarios avanzados)**. Es la opción recomendada para asegurar que la persistencia funcione correctamente y para guardar tus cambios en refugiOS.
        ```bash
        sudo add-apt-repository ppa:mkusb/ppa
        sudo apt update
        sudo apt install mkusb usb-pack-efi
        ```

*   **Desde Debian:**
    Debido a que las versiones modernas de Debian (12, 13 y superiores) tienen políticas de seguridad estrictas que bloquean repositorios antiguos, realizaremos una instalación manual:
    1. **Instalación de los paquetes necesarios:**
       Descarga los archivos `.deb` (busca siempre la versión más reciente) de **dus**, **mkusb-common**, **mkusb-nox** y **usb-pack-efi** desde el [repositorio oficial de mkusb](https://ppa.launchpad.net/mkusb/ppa/ubuntu/pool/main/m/mkusb/).
       
       Abre una terminal en tu carpeta de descargas e instálalos todos a la vez:
       ```bash
       sudo apt update
       sudo apt install ./dus_*.deb ./mkusb-common_*.deb ./mkusb-nox_*.deb ./usb-pack-efi_*.deb
       ```

#### Guía de uso de mkusb/dus (Común para Ubuntu y Debian)
Si has elegido la opción de instalar **mkusb**, sigue estos pasos exactos en la herramienta:

1.  **Inicio:** Ejecuta `sudo dus` en la terminal.
2.  **Acción:** Selecciona `i: Install (make a boot device)`.
3.  **Selección de imagen:** Elige el archivo `.iso` de Xubuntu que has descargado.
4.  **Selección de destino:** Marca tu pendrive. (**¡Atención!** Verifica por el tamaño que no estás marcando tu disco duro principal).
5.  **Método (Tool):** Selecciona `p: 'dus-Persistent', classic dus method`.
6.  **Opciones adicionales:** Para cualquier decisión que no se haya indicado aquí, selecciona siempre **"Use defaults"**.
7.  **Espacio de Persistencia:** Aquí debes tomar una decisión:
    - **100% (Recomendado):** Si quieres usar todo el pendrive para refugiOS y sus archivos.
    - **50%:** Si quieres que la mitad del USB sea una partición de datos común (`usbdata`) visible desde cualquier sistema operativo (estos datos **no** estarán encriptados, así que no deberías tener información personal allí).
8.  **Confirmación:** Aparecerá una pantalla de advertencia final (fondo rojo/naranja). Selecciona **Go (Yes)** y pulsa Aceptar.
*   **Otros Linux (Manual con `dd`): (no recomendado)**
    Si grabas la imagen directamente, deberas crear la partición de datos y configurar el arranque a mano:
    ```bash
    # 1. Grabar ISO (sdX es tu USB)
    sudo dd if=xubuntu-minimal.iso of=/dev/sdX bs=4M status=progress
    # 2. Crear partición con fdisk
    sudo fdisk /dev/sdX
    # (Pulsar 'n' para nueva, 'p' primaria, '3' para el número, 'Enter' a todo y 'w' para guardar)
    # 3. Formatear con la etiqueta obligatoria "writable"
    sudo mkfs.ext4 -L writable /dev/sdX3
    ```
    > **Importante:** Al arrancar por primera vez desde un USB creado con `dd`, verás el menú de inicio (GRUB). Debes pulsar la tecla **`e`**, buscar la línea `linux` y añadir la palabra `persistent` antes de los tres guiones `---`. Pulsa **F10** para arrancar.
    > 
    > Para evitar hacer esto cada vez tendrás que editar el arranque del sistema portable, un proceso técnico que detallamos en la **[Sección 3 de la Guía de Virtualización](Guia-Virtualizacion-y-Pendrive-ES#3-estabilización-de-la-persistencia-en-el-arranque-grub-dentro-de-la-imagen)**. Por eso, se recomienda usar Rufus o mkusb excepto que sepas muy bien lo que estás haciendo y te sientas cómodo con la línea de comandos.

### Opción B: Instalación Nativa (Solo expertos)
No recomendamos este método en USBs convencionales porque el "journaling" de Linux los destruirá en pocos meses. **Úsalo solo si tienes un SSD por USB.**

1.  Crea un USB instalador normal.
2.  **CONSEJO TÉCNICO:** Desconecta los discos internos de tu PC antes de empezar. Si no lo haces, el instalador de Ubuntu podría "secuestrar" el arranque de tu Windows y estropear el inicio de tu ordenador principal.
3.  Instala Xubuntu eligiendo el SSD USB como destino y activa el cifrado de disco completo (LUKS) si lo deseas.

---

## 3. Pruebas, Virtualización y Volcado

Si quieres montar RefugiOS en una imagen de disco local antes de tocar el pendrive físico, o si prefieres probar que todo funciona correctamente en una máquina virtual antes de reiniciar tu PC:

*   👉 **[Guía de Virtualización y Preparación de Pendrive](Guia-Virtualizacion-y-Pendrive-ES)**

Esta guía exhaustiva te enseñará a crear una imagen `.img`, instalar el sistema dentro de una VM (como VirtualBox o QEMU) y volcar el resultado final al USB de forma segura.

Ésta es la opción recomendada para usuarios avanzados, ya que permite trabajar en local de manera muchísimo más rápida, y luego volcar el resultado final al USB de forma segura. Es perfecta además si quieres preparar una tanda de dispositivos USB de tamaño similar.

> [!NOTE]
> Si prefieres generar la imagen de refugiOS desde cero sin depender de una ISO de Xubuntu, consulta la **[Guía de Construcción de Imagen de Sistema](Construccion-Imagen-Sistema-ES.md)**. Este método produce un sistema nativo basado en Debian Bookworm con XFCE y ofrece mejor rendimiento y menor desgaste del dispositivo.

---

## 4. Primer arranque e Instalación de refugiOS

Apaga tu PC y arranca desde el USB (F12/F8/Esc).

1.  **Configuración del teclado (Español):** 
    Por defecto, la sesión "Live" arranca en inglés. Para poner el teclado en español:
    *   Haz clic en el **menú de aplicaciones** (esquina superior izquierda).
    *   Ve a **Settings** -> **Keyboard**.
    *   En la pestaña **Layout**, desactiva la opción **"Use system defaults"**.
    *   Pulsa en **+ Add**, busca **Spanish** y dale a OK.
    *   (Opcional) Puedes subir "Spanish" arriba del todo o borrar "English" para que sea el teclado por defecto.
    
2.  **Lanzar el Instalador:** Una vez dentro del escritorio de Xubuntu, conéctate a la red y pega esto en la terminal:
    ```bash
    sudo apt install curl -y
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
    ```
2.  **Configuración:** El asistente detectará tu hardware y te sugerirá las mejores bibliotecas ZIM para tu capacidad.

Al finalizar, tu dispositivo refugiOS será **totalmente autónomo**, privado y capaz de funcionar sin Internet para siempre.

---

## Anexo: Compatibilidad con equipos antiguos (BIOS / MBR)

Si intentas arrancar refugiOS en un ordenador antiguo (aproximadamente de antes de 2012) y el USB no aparece en el menú de arranque o no es reconocido como unidad de inicio, es probable que tu equipo utilice el sistema **BIOS** tradicional en lugar del moderno **UEFI**.

En estos casos, el USB debe estar configurado con una **Tabla de Particiones MBR** (Master Boot Record) para ser detectado.

### Soluciones según tu herramienta de creación:

#### 1. Desde Windows (Rufus)
Rufus es la herramienta que ofrece más control manual sobre este aspecto. Para forzar la compatibilidad con equipos antiguos:
*   En **Esquema de partición**, selecciona **MBR**.
*   En **Sistema de destino**, selecciona **BIOS (o UEFI-CSM)**.
*   El resto de opciones (Persistencia, ISO) se mantienen igual.

#### 2. Desde Linux (mkusb / dus)
**mkusb** es la herramienta más robusta para hardware antiguo. Por defecto, crea unidades **híbridas** que contienen tanto el arranque UEFI como el arranque BIOS (MBR), por lo que suele funcionar "a la primera" en casi cualquier equipo sin ajustes adicionales.
*   Si el equipo es extremadamente antiguo, asegúrate de elegir el método `p: 'dus-Persistent', classic dus method`, ya que es el que mejor gestiona la compatibilidad heredada.

#### 3. Creador de discos de arranque / comando `dd`
Estas herramientas funcionan clonando la imagen ISO de forma literal.
*   Dado que las imágenes oficiales de Xubuntu son **isohybrid**, incluyen soporte básico para BIOS y UEFI de fábrica. 
*   Sin embargo, si tu placa base antigua tiene una implementación de arranque muy estricta, estas herramientas podrían fallar. En ese caso, la solución definitiva es usar **mkusb**.

> [!TIP]
> **¿Cómo saber si mi PC necesita MBR?**
> Si al encender el ordenador ves el logo de la marca y un texto que dice *"Press F2 for Setup"* o *"F12 for Boot Menu"*, pero la interfaz de esa configuración parece de finales de los 90 (solo texto, sin soporte para ratón), casi con seguridad necesitas una unidad preparada para **BIOS/MBR**.
