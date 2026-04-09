# Comparativa: ¿Por qué refugiOS?

Existen varias soluciones diseñadas para guardar información y herramientas útiles en caso de emergencia. Sin embargo, muchas de ellas tienen limitaciones técnicas que refugiOS intenta resolver.

---

## 1. Otras soluciones en el mercado

### Project N.O.M.A.D.
Es una plataforma muy completa y visualmente atractiva que incluye Wikipedia, herramientas médicas e Inteligencia Artificial.
*   **Limitación:** Funciona mediante "contenedores" (Docker). Esto significa que necesitas un ordenador con un sistema operativo ya instalado y funcionando perfectamente para poder usarlo. Si el disco duro de tu ordenador se rompe, no podrás acceder a la información. Además, requiere un procesador muy potente y mucha memoria RAM.

### Internet-in-a-Box (IIAB)
Es el proyecto de referencia para llevar bibliotecas escolares a zonas remotas sin Internet.
*   **Limitación:** Está diseñado principalmente para funcionar en dispositivos pequeños como Raspberry Pi y actuar como un router Wi-Fi al que otros se conectan. No está pensado para ser usado como un sistema operativo de escritorio completo en cualquier ordenador.

### Prepper Disk / Survival SSD
Son unidades USB o discos SSD que se venden ya configurados con miles de manuales y guías de supervivencia.
*   **Limitación:** A menudo son solo "almacenes" de archivos. Si el ordenador donde los conectas no tiene los programas adecuados para abrir esos archivos (como lectores de mapas o de enciclopedias ZIM), el disco no sirve de nada. Además, suelen tener precios muy elevados.

---

## 2. Otros Linux autoarrancables

### Tails (The Amnesic Incognito Live System)

Es el sistema de referencia para privacidad extrema y anonimato en la red.
*   **Limitación:** Está diseñado para "no dejar rastro" (es amnésico), lo que dificulta guardar documentos vitales de forma permanente sin una configuración compleja. Carece por defecto de la biblioteca de supervivencia offline y la IA local que refugiOS permite integrar.

### Distros ultraligeras (Puppy Linux / AntiX)

Famosas por revivir hardware antiguo debido a su bajo consumo de recursos.
*   **Limitación:** Se entregan como un lienzo en blanco. Un usuario en una emergencia tendría que dedicar horas a configurar manualmente los mapas, lectores y modelos de IA. También, pueden tener un soporte hardware más limitado y no son adaptables a sistemas como Raspberry OS. En general son perfectas para un usuario con conocimientos y tiempo para analizar e integrar los módulos disponibles, especialmente si tienes limitado el espectro de dispositivos donde planeas usarla, pero no son para la mayoría de usuarios.

---

## 3. Las ventajas de refugiOS

refugiOS ha sido diseñado para superar estos obstáculos siguiendo una filosofía de **"arrancar y listo"**.

### ¿En qué se diferencia?

1.  **Transformación Integral del Sistema:**
No es solo un USB con archivos. refugiOS es una herramienta que personaliza sistemas como Xubuntu o Raspberry Pi OS para que funcionen de forma independiente y optimizada desde un pendrive.

2.  **Entorno "Listo para el Desastre":**
Todas las herramientas (lectores de mapas, enciclopedias, inteligencia artificial) quedan instaladas y configuradas por el script. No tienes que instalar nada manualmente en el sistema final.

3.  **Máximo rendimiento en equipos modestos:**
Al optimizar directamente el sistema operativo base (como Xubuntu), refugiOS aprovecha al máximo la potencia del hardware sin capas intermedias como Docker. Esto permite que la IA y los mapas funcionen rápido incluso en portátiles antiguos.

4.  **Seguridad y Persistencia:**
Implementa herramientas de cifrado profesional (LUKS) para proteger tus documentos personales, permitiendo que la información crítica sobreviva a los reinicios de forma segura.

5.  **Gratuito, Abierto y Auditable:**
Es un proyecto de código abierto. Cualquier persona puede auditar los scripts de personalización, ver qué cambios se realizan y crear su propio dispositivo de emergencia sin depender de terceros.
