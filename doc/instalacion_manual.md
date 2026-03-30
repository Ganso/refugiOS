# Guía Técnica de Preparación de refugiOS

Esta guía explica en detalle cómo preparar tu unidad de refugiOS desde cualquier sistema operativo (Windows o Linux).

## 1. Elección del hardware (El soporte)

Antes de empezar, de tu hardware dependerá la velocidad y vida útil de tu refugio:

*   **Recomendación de Oro:** Aunque un pendrive estándar funciona, lo ideal para un buen rendimiento es un **disco SSD de bolsillo** (o un adaptador USB para discos M.2 NVMe). Las memorias USB baratas se desgastan rápido bajo el uso constante de Linux y su velocidad de escritura es muy pobre.
*   **Capacidad y Contenido:**
    *   **16 GB (Mínimo absoluto):** Sistema base + WikiMed + Mapas básicos + IA ligera. Sin espacio para Wikipedia.
    *   **32 GB (Equilibrado):** Todo lo anterior + Wikipedia "Mini" (solo texto o imágenes reducidas).
    *   **64 GB (Estándar):** ¡El punto ideal! Incluye la **Wikipedia completa con imágenes**, modelo IA Phi-3.5 y mapas detallados.
    *   **128 GB o más:** Permite bibliotecas masivas (Survivor Library), mapas de todo el mundo y múltiples modelos de IA.

> [!TIP]
> **Consejos de compra (¿Qué buscar?):**
> *   **Versión de USB:** Busca siempre **USB 3.0, 3.1 o 3.2** (a veces marcados como "Gen 1" o "Gen 2"). El conector suele ser de color azul o rojo por dentro.
> *   **Velocidad:** En la caja, busca velocidades de lectura superiores a **150 MB/s** y de escritura superiores a **50 MB/s**.
> *   **Formato:** Los de carcasa metálica disipan mejor el calor durante un uso intensivo.
>
> **⚠️ Qué evitar:**
> *   **USB 2.0:** Es desesperadamente lento para ejecutar un sistema operativo. Un arranque que tarda 30 segundos en USB 3.0 puede tardar 10 minutos en USB 2.0.
> *   **Marcas desconocidas:** Huye de ofertas "demasiado buenas para ser verdad" de 1 TB por 10€; suelen ser estafas con capacidad real ínfima.
>
> **Estrategia de respaldo:**
> Si tienes pendrives antiguos o más pequeños (16 GB), no los tires. Puedes dejarlos como **unidades de reserva** metidos en una mochila, en el botiquín o en el vehículo con el sistema básico. Lleva siempre contigo "el bueno" (SSD o USB 3.2 rápido) como unidad principal.

### ¿Cómo distinguir un SSD de un Pendrive?
Es fácil confundirlos por el nombre, pero su rendimiento es abismal:
*   **Pendrive (Memoria USB):** Es del tamaño de un pulgar, muy ligero y barato. Se calienta mucho y su velocidad cae drásticamente tras 5 minutos de uso.
*   **SSD de bolsillo:** Es algo más grande (como un mechero o una caja de cerillas), suele tener carcasa de metal y velocidades que no bajan de los 400 MB/s. Es una unidad de disco real, pero miniaturizada.

### Qué pedir en la tienda (o buscar en Amazon)
Si vas a una tienda física o buscas online, usa estas palabras mágicas para no fallar:
*   **En tienda física:** *"Quiero un disco SSD externo de bolsillo, que sea USB 3.2 y de al menos 64GB (o 128GB), con velocidad de lectura superior a 400 MB/s"*.
*   **En tiendas online:** Busca *"SSD Portátil 128GB USB 3.2"* o *"Unidad de estado sólido externa USB-C"*. Fíjate que en la descripción ponga **"SSD"** y no solo "Flash Drive" o "USB Stick".

---

## 2. Descarga de la imagen base (El software)

Utilizamos versiones ligeras de Xubuntu para maximizar el espacio libre disponible:

*   [**Xubuntu 24.04 LTS (Recomendado)**](https://xubuntu.org/): La opción más estable con soporte garantizado durante años.
*   [**Xubuntu 25.10 (Última versión)**](https://xubuntu.org/): Si prefieres tener kernels más modernos para hardware muy nuevo, aunque con un ciclo de soporte más corto.
*   **Aviso:** Descarga siempre la variante **"Minimal"** para ahorrar unos 2 GB de espacio eliminando programas innecesarios (juegos, ofimática pesada, etc.).

---

## 3. Creación de la unidad de arranque

Hay dos formas principales de configurar el sistema. Lee con atención:

### Opción A: USB "Live" con Persistencia (Recomendado)
El sistema reside de forma segura en una imagen inerte (SquashFS) y los cambios se guardan en la partición `writable`. Esto evita el desgaste excesivo de la memoria y protege tu ordenador anfitrión.

*   **Desde Windows:** Usa [**Rufus**](https://rufus.ie/). Al elegir la ISO, arrastra el deslizador de **"Tamaño de partición persistente"** al máximo posible (dejando un poco de aire).
*   **Desde Ubuntu:** Usa la herramienta nativa **"Creador de discos de arranque"**.
*   **Desde Debian (usando `mkusb`):**
    Para instalar `mkusb` en Debian debes añadir sus llaves y repositorio:
    ```bash
    sudo apt install dirmngr
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 54B8C8AC
    echo "deb http://ppa.launchpad.net/mkusb/ppa/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/mkusb.list
    sudo apt update && sudo apt install mkusb usb-pack-efi
    ```
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
    > Para evitar hacer esto cada vez tendrás que editar el arranque del sistema portable, lo cual está fuera del acance de esta guía. Por eso, se recomienda usar Rufus o mkusb excepto que sepas muy bien lo que estás haciendo y te sientas cómodo con la línea de comandos.

### Opción B: Instalación Nativa (Solo expertos)
No recomendamos este método en USBs convencionales porque el "journaling" de Linux los destruirá en pocos meses. **Úsalo solo si tienes un SSD por USB.**

1.  Crea un USB instalador normal.
2.  **CONSEJO TÉCNICO:** Desconecta los discos internos de tu PC antes de empezar. Si no lo haces, el instalador de Ubuntu podría "secuestrar" el arranque de tu Windows y estropear el inicio de tu ordenador principal.
3.  Instala Xubuntu eligiendo el SSD USB como destino y activa el cifrado de disco completo (LUKS) si lo deseas.

---

## 4. Pruebas y Virtualización

Si quieres probar que el USB funciona correctamente antes de reiniciar tu PC principal:

*   **Bajo Windows:** Puedes usar [**VMware Player**](https://www.vmware.com/products/workstation-player.html) o [**VirtualBox**](https://www.virtualbox.org/) añadiendo el USB físico como disco duro de la máquina virtual.
*   **Bajo Linux ([QEMU](https://www.qemu.org/)):** Es el método más rápido para desarrolladores:
    ```bash
    sudo apt install qemu-system-x86 qemu-kvm ovmf
    sudo qemu-system-x86_64 -enable-kvm -m 4096 -bios /usr/share/ovmf/OVMF.fd -drive file=/dev/sdX,format=raw
    ```

---

## 5. Primer arranque e Instalación de refugiOS

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
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
    ```
2.  **Configuración:** El asistente detectará tu hardware y te sugerirá las mejores bibliotecas ZIM para tu capacidad.

Al finalizar, tu dispositivo refugiOS será **totalmente autónomo**, privado y capaz de funcionar sin Internet para siempre.
