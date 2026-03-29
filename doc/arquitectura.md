# Arquitectura del Sistema Operativo y Ecosistema Técnico

Para asegurar la disponibilidad de refugiOS en los perores escenarios posibles, resulta imperativo tomar decisiones muy austeras respecto al _bloatware_ sin sacrificar la versatilidad de las bibliotecas de Linux estándares.

## 1. Entorno Base (El Vehículo de la Persistencia)

*   **Familia Tecnológica:** Sistema operativo Linux.
*   **Distribución Optimizada:** **Xubuntu LTS**, la variante oficial y reconocida de Canonical enfocada a los equipos de gama baja a través del entorno de escritorio **XFCE**. 
*   **Gestión de Memoria:** Un escritorio de XFCE 4.18 apenas utiliza un 15% del procesador y **menos de 1 GB de RAM al ralentí**. En un escenario preapocalíptico, esta agilidad marca la diferencia para equipos portátiles alimentados con diminutos cargadores solares y prolonga la curva de consumo hasta el apagado. 

Existen dos distribuciones óptimas actualmente testeadas y funcionales como la escorrentía maestra del sistema:
*   **Xubuntu 24.04 LTS Desktop:** Al disponer de un soporte a largo plazo (Long Term Support), asegura estabilidad en las instalaciones, con mitigación de bugs subyacentes bien depurados por un trienio mínimo.
*   **Xubuntu 25.10 Minimal (Core):** Carece de suites de paquetería como videojuegos y editores pesados ya preinstalados, bajando la carga de memoria ISO hasta los \~1.8GB, ahorrando una grandísima porción de almacenamiento para la enciclopedia Wikipedia y persistencia de memoria USB en discos pequeños.

La arquitectura persigue por principio filosófico utilizar un sistema _estándar general_ para reducir drásticamente el punto de falla técnico, facilitando reparaciones mediante conocimientos comunes entre entusiastas informáticos o de radiocomunicación del área.

---

## 2. Desglose de la Internacionalización Dinámica (i18n)

Poder ejecutar una estación de supervivencia que hable de forma obligatoria un solo dialecto, limitaría su propagación como estandarte de ayuda global.

Ubuntu fue seleccionado no solo por hardware, sino por poseer uno de los diccionarios de la línea de comandos de internacionalización más robustos del mercado: **`check-language-support`**.

El asistente post-instalación está obligado a detectar (o requerir) un código corto como entrada, como *fr* (Francia), *en* (Inglaterra) o *es* (Hispanoamérica). El instalador autómata, desde nuestro shell de despliegue principal `install.sh`, invoca las macros nativas para localizar las dependencias asociadas a esa designación:

```bash
sudo apt-get install $(check-language-support -l <CÓDIGO_IDIOMA>)
```

De este modo —con la máquina base conectada por última vez a Internet frente al portador— se compilan en vivo todas las transiciones como:
*   Teclados alfanuméricos adaptados con diacríticos.
*   Paquetes de libreoffice-l10n en ese idioma.
*   Traducciones de sistema locales (Hunspell dict, Man pages).
*   Diccionarios tipográficos en los renderizadores PDF o lectores ZIM.
*   Localización en los motores del modelo Large Language offline.

Y así el sistema mutará su GUI adaptándose al refugiado que preparó la distribución y a su región local, descartando del espacio todo el lastre de dialectos no relacionados que ocuparían datos de supervivencia.

---

## 3. Filosofía "Bare Metal" vs Contenedores 

Un hilo conductor arquitectónico vital de refugiOS contra sistemas similares (como Project NOMAD) es su aversión al uso hipervisores de virtualización encapsulada. 

La arquitectura prioriza en un 100% las ejecuciones binarias compiladas de manera estática y las aplicaciones modulares sin intermediarios, para no recargar procesos con Daemons y máquinas puente:
*   El software se provee en forma de **AppImages** genéricas y autocontenidas (`chmod +x app.AppImage`), de forma que los binarios porten internamente todo el árbol referenciado de dependencias.
*   Ejecutables compilados a la versión universal del procesador (`.exe` y `.sh` monolíticos), como es el caso de Llamafile (utilizando compresión polyglota como ejecutable de Bash/ZSH y PE para el vector hardware).
*   Configuraciones a nivel de directorio de entorno de usuario (`.config`, `/opt/refugiOS/`).
*   Los contenedores de seguridad se implementan a más bajo nivel operando directamente un subsistema lógico del disco mediante la interceptación segura (Cifrado en **Linux Unified Key Setup LUKS**).
