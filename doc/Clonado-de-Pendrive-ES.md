# Guía de Clonado de Unidades refugiOS

Si ya has configurado tu primer pendrive de **refugiOS** y quieres hacer una copia exacta para un familiar, un amigo o simplemente para tener un respaldo de seguridad, esta guía te explica cómo clonarlo paso a paso.

## 1. Clonado en Windows

Para clonar un pendrive en Windows, la herramienta más sencilla y fiable es **HDD Raw Copy Tool**.

1.  Descarga e instala [HDD Raw Copy Tool](https://hddguru.com/software/HDD-Raw-Copy-Tool/) (hay una versión portable que no requiere instalación).
2.  Conecta tu pendrive de refugiOS (Origen) y el nuevo pendrive (Destino).
3.  Abre el programa:
    *   **SOURCE (Origen):** Selecciona tu pendrive de refugiOS actual. Haz clic en *Continue*.
    *   **TARGET (Destino):** Selecciona el nuevo pendrive donde quieres volcar la copia. **¡Cuidado! Se borrará todo lo que haya en él.** Haz clic en *Continue*.
4.  Haz clic en **START** y espera a que termine el proceso.

## 2. Clonado en Ubuntu y derivados (Linux)

En Linux tienes dos opciones: una gráfica y otra por terminal.

### Opción A: Utilidad de Discos (Gráfico)
Es la forma más segura para evitar errores al escribir nombres de dispositivos.

1.  Busca y abre la aplicación **Discos** (gnome-disks).
2.  Selecciona tu pendrive de refugiOS en la columna de la izquierda.
3.  Haz clic en el menú de los tres puntos (arriba a la derecha) y elige **Crear imagen del disco...**. Guárdala en tu ordenador.
4.  Una vez creada, desconecta el pendrive original y conecta el nuevo.
5.  Selecciona el nuevo pendrive en la lista, pulsa de nuevo los tres puntos y elige **Restaurar imagen del disco...**. Selecciona el archivo que acabas de crear.

### Opción B: Terminal (Comando `dd`)
Es el método más rápido pero **requiere mucha precaución**. Un error en las letras de los discos puede borrar tu disco duro principal.

1.  Identifica tus unidades con `lsblk`. Supongamos que `/dev/sdb` es el origen y `/dev/sdc` el destino.
2.  Ejecuta el comando para copiar bit a bit:
    ```bash
    sudo dd if=/dev/sdb of=/dev/sdc bs=64K conv=noerror,sync status=progress
    ```

---

## 3. ¿Qué pasa si los tamaños son distintos?

Es muy común que dos pendrives que dicen ser de "64GB" tengan en realidad unos pocos megabytes de diferencia.

### Caso A: El destino es MÁS GRANDE que el origen
El proceso de clonado funcionará perfectamente, pero verás que en el nuevo pendrive "sobra" espacio al final que no puedes usar.
*   **Solución:** Abre la herramienta **GParted** en Linux o el **Administrador de discos** en Windows y expande la última partición (`writable` o la de datos) para ocupar todo el espacio restante.

### Caso B: El destino es MÁS PEQUEÑO que el origen
Aunque solo sea por un MB, el clonado fallará o dejará una unidad corrupta al final.
*   **Solución:** Antes de clonar, debes **reducir el tamaño de la última partición** del pendrive original.
    1. Usa **GParted** para encoger la partición de datos del origen de modo que el tamaño total de las particiones sea menor que la capacidad del pendrive destino.
    2. Realiza el clonado normalmente.
    3. Una vez clonado, puedes volver a expandir la partición en ambos pendrives si lo deseas.

---

> [!TIP]
> **Consejo de Resiliencia:** 
> Tener una copia de seguridad física es vital. Si tu pendrive principal se pierde o se daña físicamente por el uso prolongado, tener un clon ya configurado te ahorrará horas de descarga e instalación en una situación de emergencia.
