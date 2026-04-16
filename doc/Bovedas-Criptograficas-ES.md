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

Para que el sistema sea fácil de usar, hemos creado tres asistentes directos en tu escritorio:

1.  **Crear Bóveda:** 
    Este asistente te guiará paso a paso. Detectará si tienes pendrives conectados y te sugerirá un tamaño basado en tus datos. Podrás elegir un nombre personalizado para cada bóveda. Al terminar, el sistema puede importar automáticamente tus archivos desde el USB.

2.  **Abrir Bóveda:** 
    Te permite seleccionar qué bóveda quieres abrir. Tras introducir la contraseña, aparecerá automáticamente un **icono en el escritorio** con el nombre de tu bóveda. Este icono te da acceso directo a tus archivos de forma segura.

3.  **Cerrar Bóveda:** 
    Al pulsar este botón, podrás elegir qué bóvedas cerrar (o cerrarlas todas a la vez). El icono del escritorio desaparecerá y tus archivos volverán a estar protegidos por cifrado profesional LUKS.


**Consejo de seguridad:** Cierra siempre tu bóveda en cuanto termines de usarla. Mientras esté abierta, cualquier persona con acceso físico a tu ordenador podría ver los archivos.
