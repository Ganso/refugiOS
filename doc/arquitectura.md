# Arquitectura del Sistema refugiOS

Para garantizar la fiabilidad de refugiOS en situaciones críticas, hemos tomado decisiones de diseño centradas en la ligereza, la compatibilidad y la facilidad de uso, sin sacrificar la potencia de Linux.

## 1. Sistema Base

*   **Sistema Operativo:** Linux.
*   **Distribución:** [**Xubuntu LTS**](https://xubuntu.org/), una versión oficial de Ubuntu que utiliza el escritorio [**XFCE**](https://www.xfce.org/). 
*   **Rendimiento:** XFCE es ideal para equipos antiguos o con recursos limitados. Un sistema recién arrancado utiliza **menos de 1 GB de RAM**, lo que permite ahorrar batería en portátiles y funcionar con fluidez en casi cualquier hardware.

### Versiones recomendadas:
*   **Xubuntu 24.04 LTS:** Ofrece estabilidad a largo plazo y soporte técnico garantizado durante años.
*   **Xubuntu 25.10 Minimal:** Es la versión "limpia" que no incluye programas innecesarios (juegos, reproductores pesados, etc.), lo que nos permite ahorrar unos 2 GB de espacio extra para contenidos útiles.

Nuestra filosofía es usar un sistema **estándar**. Esto significa que cualquier persona con conocimientos básicos de Linux podrá reparar o mejorar el sistema fácilmente sin necesidad de herramientas raras o propietarias.

---

## 2. Idiomas y Adaptación (Internacionalización)

refugiOS está diseñado para ser global. El instalador detecta automáticamente el idioma de tu sistema o permite elegirlo manualmente.

Utilizamos herramientas nativas de Ubuntu (`check-language-support`) para que, durante la preparación, el sistema descargue solo lo necesario:
*   Configuración del teclado local.
*   Traducciones de las aplicaciones y del sistema.
*   Diccionarios para los lectores de documentos.
*   Idiomas compatibles para el asistente de Inteligencia Artificial.

De este modo, el sistema se adapta completamente a tu región sin ocupar espacio innecesario con idiomas que no vas a utilizar.

---

## 3. Filosofía de Software: Simplicidad y Portabilidad

A diferencia de otros proyectos que usan sistemas complejos de virtualización o "contenedores" pesados, refugiOS apuesta por aplicaciones directas y portátiles:

*   **AppImages:** Son aplicaciones que no necesitan instalación. Todo lo necesario para que funcionen está dentro de un solo archivo.
*   **Ejecutables estáticos:** Como el motor de IA ([Llamafile](https://github.com/Mozilla-Ocho/llamafile)), que funciona simplemente haciendo doble clic, sin configuraciones complicadas.
*   **Bóvedas de seguridad:** Para proteger tus archivos personales, utilizamos el estándar de cifrado de disco de Linux ([**LUKS**](https://gitlab.com/cryptsetup/cryptsetup)), que es extremadamente seguro y compatible.

Este enfoque asegura que el software sea robusto, fácil de mover entre dispositivos y que consuma el mínimo posible de recursos de tu ordenador.
