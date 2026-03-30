# Configuración de Persistencia (Desde el Anfitrión)

Si quieres que refugiOS guarde tus cambios para siempre sin tener que escribir `persistent` en cada arranque, lo más sencillo es configurar la persistencia **en el momento de crear el USB desde tu sistema principal (Windows o Linux)**. 

Intentar parchear un USB ya creado con `dd` es muy difícil porque la partición de arranque es de solo lectura. **Lo mejor es volver a grabarlo siguiendo estos pasos:**

---

## 🟦 Desde Windows (Método con Rufus)

Rufus es la herramienta más sencilla y fiable para activar la persistencia en segundos:

1.  Abre [**Rufus**](https://rufus.ie/).
2.  Selecciona tu dispositivo USB y la imagen ISO de Xubuntu.
3.  **¡CLAVE!:** Busca el deslizador **"Tamaño de partición persistente"** (Persistence partition size). Arrástralo hacia la derecha para asignar el espacio que desees (recomendado: el máximo disponible).
4.  Pulsa **Empezar**. Rufus creará automáticamente la estructura necesaria para que el sistema reconozca la persistencia sin tocar nada más.

---

## 🐧 Desde Linux (Método con mkusb)

Si usas Linux, la herramienta estándar de creación de discos no suele soportar persistencia. **mkusb** es la solución definitiva:

1.  **Instalar mkusb:** (Si usas Debian/Ubuntu)
    ```bash
    sudo add-apt-repository ppa:mkusb/ppa && sudo apt update
    sudo apt install mkusb usb-pack-efi
    ```
2.  Ejecuta **`dus`** (la interfaz moderna de mkusb) desde la terminal o el menú.
3.  Selecciona la opción **'i' (Install)** y luego **'p' (Persistent live)**.
4.  Sigue el asistente para elegir tu ISO y tu pendrive. El programa se encargará de crear una partición `writable` y configurar el menú GRUB por ti.

---

## 🛠️ ¿Y si ya lo grabé con `dd` y no quiero repetir?

Si ya tienes un USB con una partición `writable` pero el arranque es de solo lectura, la única forma de no escribir `persistent` a mano es:

1.  **En Windows/Linux:** Abre el USB y busca la partición pequeña llamada **ESP** o **EFI**.
2.  Crea una carpeta (si no existe) en `EFI/boot/`.
3.  Crea un archivo de texto llamado **`grub.cfg`** dentro de esa carpeta con este contenido (avanzado):
    ```bash
    set prefix=(memdisk)/boot/grub
    set root=(memdisk)
    configfile /boot/grub/grub.cfg
    ```
    *Nota: Este método puede fallar dependiendo de la versión exacta de la ISO. Lo más recomendable sigue siendo **Rufus** o **mkusb**.*
