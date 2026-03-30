# Bóvedas de Archivos (Seguridad y Cifrado)

En situaciones de crisis o traslados, es posible que tu dispositivo refugiOS pueda ser confiscado o robado. Si guardas fotos de documentos (DNI, pasaportes), información médica o claves bancarias sin protección en un USB, cualquier persona que lo encuentre tendrá acceso total a tu vida privada.

Para evitar esto, refugiOS incluye un sistema de **Bóvedas Seguras** que mantienen tus archivos personales cifrados y ocultos.

## ¿Qué es una Bóveda Segura?

En lugar de proteger todo el pendrive con una contraseña (lo cual puede ser lento o dar problemas de compatibilidad), refugiOS utiliza "contenedores cifrados". 

Un contenedor es un archivo especial (por ejemplo, `mis_datos.img`) que funciona como una caja fuerte. Solo puedes ver lo que hay dentro si conoces la contraseña correcta.

### Características principales:
*   **Estándar Profesional:** Utilizamos [**LUKS**](https://gitlab.com/cryptsetup/cryptsetup) (Linux Unified Key Setup), el mismo sistema de cifrado que usan los gobiernos y empresas en Linux. Es extremadamente seguro.
*   **Modularidad:** Puedes tener varias bóvedas distintas (una para temas médicos, otra para documentos legales) con contraseñas diferentes.
*   **Rapidez:** Puedes abrir y cerrar tus archivos en segundos.

---

## Cómo funcionan las Bóvedas en refugiOS

Para que el sistema sea fácil de usar, hemos creado tres botones directos en tu escritorio:

1.  **Crear Bóveda:** 
    La primera vez que uses el sistema, este botón te guiará para crear tu archivo seguro. Te pedirá que elijas una **contraseña fuerte** (¡no la olvides, si la pierdes no podrás recuperar tus archivos!). El sistema creará un espacio reservado de unos 3 GB para tus documentos.

2.  **Abrir Bóveda:** 
    Al hacer doble clic, se abrirá una pequeña ventana pidiéndote tu contraseña. Si es correcta, aparecerá una carpeta llamada **MIS_DATOS_SECRETOS** en tu escritorio. Ahí puedes copiar, pegar y editar tus archivos con normalidad.

3.  **Cerrar Bóveda:** 
    Cuando termines de trabajar, pulsa este botón. La carpeta desaparecerá automáticamente del escritorio y tus archivos volverán a estar cifrados y protegidos. Nadie podrá verlos aunque conecten el USB a otro ordenador.

**Consejo de seguridad:** Cierra siempre tu bóveda en cuanto termines de usarla. Mientras esté abierta, cualquier persona con acceso físico a tu ordenador podría ver los archivos.
