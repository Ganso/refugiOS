# Visión y Experiencia del Usuario

Este documento explica qué es **refugiOS**, para qué sirve y cómo es la experiencia de usarlo, tanto al prepararlo como en una situación de emergencia.

## 1. ¿Qué es refugiOS?

El nombre combina "Refugio" y "OS" (Sistema Operativo). Queremos que sea un **refugio digital**: un lugar seguro donde guardar conocimientos, mapas y documentos importantes para cuando las redes normales (Internet, electricidad, telefonía) fallen.

Es una herramienta diseñada para funcionar siempre **sin conexión** (100% offline).

### Casos de uso principales:
*   **Desastres naturales:** Terremotos o inundaciones que cortan las comunicaciones durante semanas.
*   **Apagones prolongados:** Fallos en la red eléctrica o de datos.
*   **Zonas remotas:** Lugares sin cobertura donde necesitas guías médicas o mapas.
*   **Privacidad extrema:** Para personas que necesitan proteger su información personal con cifrado profesional.

En resumen: refugiOS convierte cualquier ordenador (incluso uno viejo o rescatado) en un centro de información y supervivencia totalmente independiente.

---

## 2. Preparación (Antes de la crisis)

El proceso de creación del dispositivo es sencillo y está pensado para que cualquier persona pueda hacerlo en casa con tranquilidad:

1.  **El soporte:** Solo necesitas un pendrive o disco SSD portátil de buena calidad.
2.  **El arranque:** Grabas una imagen de Linux (Xubuntu) en el USB siguiendo nuestra guía.
3.  **El instalador:** Arrancas el ordenador desde ese USB y ejecutas un solo comando.
4.  **Configuración guiada:** Aparecerá un menú sencillo que te preguntará:
    *   Tu idioma preferido.
    *   Qué contenidos quieres descargar (Wikipedia completa, manuales médicos, etc.) según el espacio de tu USB.
    *   Qué mapas de qué regiones del mundo necesitas.
5.  **Tu Bóveda Personal:** El sistema te ayudará a crear una carpeta segura con contraseña para que guardes tus fotos, pasaportes, recetas médicas y documentos importantes.

---

## 3. Uso en situación de emergencia

Cuando ocurre un problema real, refugiOS está diseñado para ser rápido, sencillo y sin complicaciones técnicas:

1.  **Arranque universal:** Conectas el USB a cualquier ordenador que funcione (incluso uno prestado o viejo alimentado por una batería solar).
2.  **Escritorio limpio:** Al encenderlo, entras directamente a un escritorio sencillo. No te pedirá contraseñas de Wi-Fi ni configuraciones raras.
3.  **Iconos claros y directos:** En el escritorio verás botones grandes para lo que necesites:
    *   **"Enciclopedia Médica":** Para saber cómo tratar una herida o identificar una enfermedad (vía [Wikipedia](https://es.wikipedia.org/)/[WikiMed](https://www.kiwix.org/)).
    *   **"Mapas":** Para encontrar fuentes de agua, refugios u hospitales sin usar Internet ni enviar tu posición a nadie (vía [Organic Maps](https://organicmaps.app/)).
    *   **"Asistente IA":** Un asistente al que puedes preguntarle cosas complejas (ej: "¿Cómo purificar agua?") y te responderá usando solo la potencia de ese ordenador (vía [Llamafile](https://github.com/Mozilla-Ocho/llamafile) y el modelo [Phi-3.5](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)).
    *   **"Mis Documentos":** Pones tu contraseña y aparecen tus archivos personales para identificarte o pedir ayuda.

refugiOS es, sencillamente, tu seguro de vida digital cuando el mundo conectado deja de funcionar.
