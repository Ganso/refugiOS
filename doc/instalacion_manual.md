# Guía Técnica de Preparación de refugiOS

Esta guía explica en detalle cómo preparar tu unidad de refugiOS desde cualquier sistema operativo (Windows o Linux).

## 1. Elección del hardware (El soporte)

Antes de empezar, de tu hardware dependerá la velocidad y vida útil de tu refugio:

*   **Recomendación de Oro:** Aunque un pendrive estándar funciona, lo ideal para un rendimiento profesional es un **disco SSD de bolsillo** (o un adaptador USB para discos M.2 NVMe). Las memorias USB baratas se desgastan rápido bajo el uso constante de Linux y su velocidad de escritura es muy pobre.
*   **Capacidad y Contenido:**
    *   **16 GB (Mínimo absoluto):** Sistema base + WikiMed + Mapas básicos + IA ligera. Sin espacio para Wikipedia.
    *   **32 GB (Equilibrado):** Todo lo anterior + Wikipedia "Mini" (solo texto o imágenes reducidas).
    *   **64 GB (Estándar):** ¡El punto ideal! Incluye la **Wikipedia completa con imágenes**, modelo IA Phi-3.5 y mapas detallados.
    *   **128 GB o más:** Permite bibliotecas masivas (Survivor Library), mapas de todo el mundo y múltiples modelos de IA.

---

## 2. Descarga de la imagen base (El software)

Utilizamos versiones ligeras de Xubuntu para maximizar el espacio libre disponible:

*   **Xubuntu 24.04 LTS (Recomendado):** La opción más estable con soporte garantizado durante años.
*   **Xubuntu 25.10 (Última versión):** Si prefieres tener kernels más modernos para hardware muy nuevo, aunque con un ciclo de soporte más corto.
*   **Aviso:** Descarga siempre la variante **"Minimal"** para ahorrar unos 2 GB de espacio eliminando programas innecesarios (juegos, ofimática pesada, etc.).

---

## 3. Creación de la unidad de arranque

Hay dos formas principales de configurar el sistema. Lee con atención:

### Opción A: USB "Live" con Persistencia (Recomendado)
El sistema reside de forma segura en una imagen inerte (SquashFS) y los cambios se guardan en la partición `writable`. Esto evita el desgaste excesivo de la memoria y protege tu ordenador anfitrión.

*   **Desde Windows:** Usa **Rufus**. Al elegir la ISO, arrastra el deslizador de **"Tamaño de partición persistente"** al máximo posible (dejando un poco de aire).
*   **Desde Ubuntu:** Usa la herramienta nativa **"Creador de discos de arranque"**.
*   **Desde Debian (usando `mkusb`):**
    Para instalar `mkusb` en Debian debes añadir sus llaves y repositorio:
    ```bash
    sudo apt install dirmngr
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 54B8C8AC
    echo "deb http://ppa.launchpad.net/mkusb/ppa/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/mkusb.list
    sudo apt update && sudo apt install mkusb usb-pack-efi
    ```
*   **Otros Linux (Manual con `dd`):**
    Si grabas la imagen directamente, deberás crear la partición de datos a mano:
    ```bash
    # 1. Grabar ISO (sdX es tu USB)
    sudo dd if=xubuntu-minimal.iso of=/dev/sdX bs=4M status=progress
    # 2. Crear partición con fdisk
    sudo fdisk /dev/sdX
    # (Pulsar 'n' para nueva, 'p' primaria, '3' para el número, 'Enter' a todo y 'w' para guardar)
    # 3. Formatear con la etiqueta obligatoria "writable"
    sudo mkfs.ext4 -L writable /dev/sdX3
    ```

### Opción B: Instalación Nativa (Solo expertos)
No recomendamos este método en USBs convencionales porque el "journaling" de Linux los destruirá en pocos meses. **Úsalo solo si tienes un SSD por USB.**

1.  Crea un USB instalador normal.
2.  **CONSEJO TÉCNICO:** Desconecta los discos internos de tu PC antes de empezar. Si no lo haces, el instalador de Ubuntu podría "secuestrar" el arranque de tu Windows y estropear el inicio de tu ordenador principal.
3.  Instala Xubuntu eligiendo el SSD USB como destino y activa el cifrado de disco completo (LUKS) si lo deseas.

---

## 4. Pruebas y Virtualización

Si usas máquinas virtuales, recuerda que refugiOS arranca en modo **UEFI**. Por eso en QEMU usamos el firmware **OVMF**, ya que la BIOS clásica (SeaBios) no reconocerá el formato del USB actual.

*   **En Linux (QEMU):**
    ```bash
    sudo apt install qemu-system-x86 qemu-kvm ovmf
    sudo qemu-system-x86_64 -enable-kvm -m 4096 -bios /usr/share/ovmf/OVMF.fd -drive file=/dev/sdX,format=raw
    ```

---

## 5. Primer arranque e Instalación de refugiOS

Apaga tu PC y arranca desde el USB (F12/F8/Esc).

1.  **Parche de Persistencia:** Si el sistema no guarda los cambios solo, al ver el menú de "Try Xubuntu", pulsa la tecla **`e`**. Busca la línea que empieza por `linux` y añade la palabra `persistent` justo antes de los tres guiones `---`. Luego pulsa **F10** o **Ctrl+X** para arrancar.
2.  **Lanzar el Instalador:** Una vez dentro del escritorio, conéctate a la red y pega esto en la terminal:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
    ```
3.  **Configuración:** El asistente detectará tu hardware y te sugerirá las mejores bibliotecas ZIM para tu capacidad.

Al finalizar, tu dispositivo refugiOS será **totalmente autónomo**, privado y capaz de funcionar sin Internet para siempre.
