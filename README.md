<h1 align="center">
  <br>
  <img src="https://via.placeholder.com/150/000000/FFFFFF/?text=refugiOS" alt="refugiOS" width="150" style="border-radius: 20px;">
  <br>
  refugiOS - Tu Refugio Digital y Biblioteca de Supervivencia
  <br>
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Estado-Desarrollo-green.svg" alt="Estado del Proyecto">
  <img src="https://img.shields.io/badge/Sistema-Xubuntu_LTS-blue.svg" alt="Sistema Operativo">
  <img src="https://img.shields.io/badge/Paradigma-Offline_First-orange.svg" alt="Sin Conexión">
  <img src="https://img.shields.io/badge/IA-Llamafile_(Local)-purple.svg" alt="IA Offline">
</p>

---

## 📖 ¿Qué es refugiOS?

**refugiOS** es un sistema operativo portátil diseñado para situaciones de emergencia, falta de Internet o necesidad extrema de privacidad. 

A diferencia de otras soluciones complejas, **refugiOS convierte cualquier ordenador normal (incluso uno antiguo) en una estación de información completa** que arranca directamente desde un pendrive USB. 

Es una herramienta pensada para tener a mano todos los conocimientos, mapas y documentos vitales de forma segura, privada y totalmente funcional sin depender de la nube.

## ✨ Características Principales

*   **⚡ Arranca en cualquier PC (Plug-and-play):** No necesitas instalar nada en el ordenador que encuentres. Conectas el USB, enciendes el equipo y ya tienes tu refugio digital funcionando a máxima velocidad.
*   **📚 Conocimiento Universal Offline:** Incluye copias completas de la Wikipedia, WikiMed (medicina), enciclopedias de supervivencia y guías de oficios gracias a la tecnología de *Kiwix*.
*   **🤖 Inteligencia Artificial Privada:** Incorpora un asistente (como ChatGPT) que funciona de forma 100% local, sin Internet. Puede ayudarte a resolver problemas técnicos, médicos o de traducción usando solo la potencia de tu ordenador.
*   **🗺️ Mapas y Navegación GPS:** Mapas detallados de todo el mundo mediante *Organic Maps*. Puedes buscar rutas y puntos de interés (fuentes, hospitales, refugios) sin emitir ninguna señal de red.
*   **🔒 Bóveda de Archivos Segura:** Sistema de cifrado profesional para guardar tus documentos más importantes (pasaportes, títulos, fotos) protegidos por una contraseña maestra.
*   **🌐 Adaptado a tu Idioma:** El sistema se configura automáticamente en tu idioma (español, inglés, francés, etc.), descargando solo los diccionarios y ayudas que necesitas.

## 🚀 Instalación Rápida

Si ya tienes un USB con una base de Linux (Xubuntu) recién instalada, solo tienes que conectar el equipo a Internet una vez y ejecutar este comando en la terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

> [!IMPORTANT] 
> **¿Aún no tienes el USB de Linux preparado?** 
> Si estás empezando de cero, sigue primero nuestra **[Guía de Instalación Manual](doc/instalacion_manual.md)** para preparar tu pendrive desde Windows o Linux.

> [!NOTE] 
> El instalador te guiará paso a paso y te preguntará qué contenidos quieres incluir según el tamaño de tu USB. Es recomendable leerla en cualquier caso.

## 📚 Documentación Detallada

Para saber más sobre cómo funciona refugiOS y cómo sacarle el máximo partido, consulta las guías en el directorio `/doc/`:

*   **[Visión y Experiencia del Usuario](doc/vision_y_experiencia.md):** El propósito del proyecto y qué esperar al usarlo.
*   **[Comparativa de Soluciones](doc/soluciones_existentes.md):** Por qué refugiOS es diferente a otras alternativas.
*   **[Aplicaciones y Software](doc/modulos_de_software.md):** Información sobre Kiwix, Mapas e Inteligencia Artificial.
*   **[Arquitectura del Sistema](doc/arquitectura.md):** Detalles técnicos sobre la base Linux y su rendimiento.
*   **[Bóvedas de Seguridad](doc/bovedas_criptograficas.md):** Cómo funciona el cifrado de tus archivos personales.

---

## 🗃️ Agradecimientos y Fuentes

refugiOS es posible gracias al increíble trabajo de proyectos de código abierto como:
*   [Xubuntu](https://xubuntu.org/) y la comunidad de Ubuntu.
*   [Kiwix](https://www.kiwix.org/) y la Wikipedia.
*   [Mozilla Ocho](https://github.com/Mozilla-Ocho/llamafile) por el motor Llamafile.
*   [Organic Maps](https://organicmaps.app/) y OpenStreetMap.
*   Modelos de lenguaje de Microsoft (Phi-3.5) y otros desarrolladores FOSS.

---
*(Este proyecto es una iniciativa de código abierto para la resiliencia digital).*