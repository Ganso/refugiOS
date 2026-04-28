<h1 align="center">
  refugiOS - Tu Refugio Digital y Biblioteca de Supervivencia
</h1>

<p align="center">
  <strong>Español 🇪🇸</strong> | <a href="README.en.md">English 🇬🇧🇺🇸</a>
</p>

<p align="center">
  <img src="logo/refugiOS.png" alt="logo de refugiOS"><br />
  <img src="https://img.shields.io/badge/Estado-Desarrollo-green.svg" alt="Estado del Proyecto">
  <img src="https://img.shields.io/badge/Versión-0.11-blue.svg" alt="Versión">
  <img src="https://img.shields.io/badge/Paradigma-Offline_First-orange.svg" alt="Sin Conexión">
  <img src="https://img.shields.io/badge/IA-Llamafile_(Local)-purple.svg" alt="IA Offline">
  <img src="https://img.shields.io/badge/Raspberry_Pi-Certificado-red.svg" alt="Raspberry Pi">
</p>

> [!WARNING]
> **Estado del Proyecto:** refugiOS se encuentra actualmente en su **primera versión Beta**. Es un proyecto en desarrollo activo y aún queda mucho camino por delante: internacionalización de la documentación, corrección de errores y la implementación de las funciones detalladas en el roadmap.

> [!IMPORTANT]
> **🚀 Guías de Instalación Rápida:**
> *   💻 **[Instalación en PC Estándar (Xubuntu)](doc/Instalacion-Xubuntu-ES.md)**
> *   🍓 **[Instalación en Raspberry Pi](doc/Instalacion-Raspberry-ES.md)**
> 
> 🌐 **Looking for the English version?** [Read the English Guide here](README.en.md) / **¿Buscas la guía en inglés?** [Consulta el manual en inglés aquí](README.en.md).

---

## 📖 ¿Qué es refugiOS?

**refugiOS** es un sistema operativo portátil diseñado para situaciones de emergencia, falta de conectividad a Internet o necesidad extrema de privacidad. 

A diferencia de otras soluciones complejas, **refugiOS convierte cualquier ordenador normal (incluso uno antiguo) en una estación de información completa** que arranca directamente desde un pendrive USB. 

También funciona en **Raspberry Pi**, convirtiéndola en una estación de información compacta, silenciosa y de bajo consumo.

Es una herramienta pensada para tener a mano todos los conocimientos, mapas y documentos vitales de forma segura, privada y totalmente funcional sin depender de la nube.

## ✨ Características Principales

*   **⚡ Arranca en cualquier PC (Plug-and-play):** No necesitas instalar nada en el ordenador que encuentres. Conectas el USB, enciendes el equipo y ya tienes tu refugio digital funcionando a máxima velocidad.
*   **🍓 Soporte nativo para Raspberry Pi:** Instalación certificada en Raspberry Pi 3B+. El instalador detecta automáticamente la arquitectura ARM y adapta todas las decisiones (paquetes APT, renderizado gráfico, etc.).
*   **📚 Conocimiento Universal Offline:** Incluye copias completas de la Wikipedia, WikiMed (medicina), enciclopedias de supervivencia y guías de oficios gracias a la tecnología de *Kiwix*.
*   **🤖 Inteligencia Artificial Privada:** Incorpora un asistente que funciona de forma 100% local, sin Internet. Puede ayudarte a resolver problemas técnicos, médicos o de traducción usando solo la potencia de tu ordenador.
*   **🗺️ Mapas y Navegación GPS:** Mapas detallados de todo el mundo mediante *Organic Maps*. Puedes buscar rutas y puntos de interés (fuentes, hospitales, refugios) sin emitir ninguna señal de red.
*   **🔒 Bóveda de Archivos Segura:** Sistema de cifrado profesional para guardar tus documentos más importantes (pasaportes, títulos, fotos) protegidos por una contraseña maestra.
*   **🌐 Adaptado a tu Idioma:** El sistema se configura automáticamente en tu idioma (español o  inglés), descargando solo los diccionarios y ayudas que necesitas.
*   Puedes ver en el apartado de **[Aplicaciones y Roadmap](doc/Modulos-y-Roadmap-ES.md)** el estado actual del proyecto, con los módulos que están ya implementados y los que se añadirán en un futuro.

### 📺 Vídeo de Demostración

<p align="center">
  <a href="https://www.youtube.com/watch?v=ZsVwWdWbtng">
    <img src="https://img.youtube.com/vi/ZsVwWdWbtng/maxresdefault.jpg" alt="refugiOS en acción" width="800">
  </a>
  <br>
  <em>refugiOS corriendo en un Ryzen 5500, arrancado desde un pendrive USB 3.2 de gama de consumo</em>
</p>

## 🚀 Instalación Rápida

### 💻 En XUbuntu (PC / Laptop)

Si ya tienes un USB con XUbuntu recién instalada, solo tienes que conectar el equipo a Internet una vez y ejecutar este comando en la terminal:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

> [!IMPORTANT] 
> **¿Aún no tienes el USB de XUbuntu preparado?** 
> Si estás empezando de cero, sigue primero nuestra **[Guía de Instalación en XUbuntu](doc/Instalacion-Xubuntu-ES.md)** para preparar tu pendrive desde Windows o Linux.

### 🍓 En Raspberry Pi

Instala primero Raspberry Pi OS con la herramienta oficial **[Raspberry Pi Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager)** y luego ejecuta el mismo instalador:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

El instalador detectará automáticamente que estás en una Raspberry Pi y adaptará todo. Consulta la **[Guía de Instalación en Raspberry Pi](doc/Instalacion-Raspberry-ES.md)** para los detalles y recomendaciones de hardware.

> [!NOTE] 
> El instalador te guiará paso a paso y te preguntará qué contenidos quieres incluir según el tamaño de tu almacenamiento.

> [!TIP]
> **¿Ya tienes tu primer pendrive listo?** Una vez que lo hayas probado y configurado a tu gusto, te recomendamos **[clonarlo a otra unidad](doc/Clonado-de-Pendrive-ES.md)** para tener una copia de seguridad o para dar copias a tus seres queridos.

> [!NOTE]
> **¿Quieres probarlo rápidamente sin tocar un pendrive?** Si tienes experiencia con máquinas virtuales, puedes montar refugiOS en una imagen de disco virtual y arrancarlo con QEMU o VirtualBox. Consulta nuestra **[Guía de Virtualización](doc/Guia-Virtualizacion-y-Pendrive-ES.md)** para los pasos detallados.


## 📱 Plataformas Recomendadas

> [!NOTE]
> refugiOS está diseñado para funcionar en una amplia gama de hardware, pero recomendamos especialmente **Xubuntu 24 LTS** y **Raspberry OS** para la mejor experiencia.
> 
> Consulta la **[Tabla de Compatibilidad Completa](doc/Compatibilidad-ES.md)** para ver todos los sistemas testados y problemas conocidos.


## 📚 Documentación Detallada

Para saber más sobre cómo funciona refugiOS y cómo sacarle el máximo partido, consulta las guías en el directorio `/doc/`:

*   **[Instalación en XUbuntu](doc/Instalacion-Xubuntu-ES.md):** Cómo preparar tu USB con XUbuntu desde Windows o Linux.
*   **[Tabla de Compatibilidad](doc/Compatibilidad-ES.md):** Distribuciones Linux y hardware certificado o en pruebas.
*   **[Instalación en Raspberry Pi](doc/Instalacion-Raspberry-ES.md):** Guía específica para Raspberry Pi con Raspberry Pi OS.
*   **[Visión y Experiencia del Usuario](doc/Vision-y-Experiencia-ES.md):** El propósito del proyecto y qué esperar al usarlo.
*   **[Comparativa de Soluciones](doc/Soluciones-Existentes-ES.md):** Por qué refugiOS es diferente a otras alternativas.
*   **[Aplicaciones y Roadmap](doc/Modulos-y-Roadmap-ES.md):** Información sobre Kiwix, Mapas e Inteligencia Artificial.
*   **[Arquitectura del Sistema](doc/Arquitectura-ES.md):** Detalles técnicos sobre la base Linux y su rendimiento.
*   **[Bóvedas de Seguridad](doc/Bovedas-Criptograficas-ES.md):** Cómo funciona el cifrado de tus archivos personales.
*   **[Clonado de Unidades](doc/Clonado-de-Pendrive-ES.md):** Cómo hacer copias exactas de tu USB en Windows o Linux.


---

## 🗃️ Agradecimientos y Fuentes

Gracias a [Felipe Monge "PlayOnRetro"](https://x.com/PlayOnRetro) por el diseño del logo.

refugiOS es posible gracias al increíble trabajo de proyectos de código abierto como:
*   [Xubuntu](https://xubuntu.org/) y la comunidad de Ubuntu para la base del sistema operativo.
*   [Raspberry Pi Foundation](https://www.raspberrypi.com/) por el hardware y el ecosistema de software ARM.
*   [Kiwix](https://www.kiwix.org/) y la [Fundación Wikimedia](https://wikimediafoundation.org/) por el acceso offline al conocimiento universal.
*   [Mozilla Ocho](https://github.com/Mozilla-Ocho/llamafile) por el motor de inferencia **Llamafile**.
*   [HuggingFace](https://huggingface.co/) y [bartowski](https://huggingface.co/bartowski) por las excelentes cuantizaciones de los modelos de IA.
*   Modelos de lenguaje **Phi-4-mini** (Microsoft) y **Qwen3** (Alibaba-Qwen).
*   [Organic Maps](https://organicmaps.app/) y los colaboradores de [OpenStreetMap](https://www.openstreetmap.org/) por la cartografía offline.
*   [Aria2](https://aria2.github.io/) para las descargas de alta eficiencia.
*   [Flatpak](https://flatpak.org/) y [Flathub](https://flathub.org/) por la distribución de aplicaciones modernas.
*   [Cryptsetup / LUKS](https://gitlab.com/cryptsetup/cryptsetup) para la seguridad y cifrado de datos personales.

---
*(refugiOS es una iniciativa de código abierto para la resiliencia digital. Actualmente en fase Beta, buscamos colaboradores para internacionalizar la documentación, migrarla a formato wiki y pulir la experiencia de usuario según nuestro [Roadmap](doc/Modulos-y-Roadmap-ES.md)).*
