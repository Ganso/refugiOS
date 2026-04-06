# Guía de Instalación en Raspberry Pi

Esta guía explica cómo instalar **refugiOS** sobre una Raspberry Pi, desde cero hasta tener el sistema completamente funcional.

> [!NOTE]
> **Plataformas certificadas:** Esta guía ha sido probada y certificada en **Raspberry Pi 3B+** con Raspberry Pi OS (64-bit, Wayland). Se buscan testers con otros modelos. Si pruebas en un modelo diferente, ¡abre una issue o contacta con el proyecto!

---

## 1. Hardware Necesario

### Raspberry Pi
- **Certificado:** Raspberry Pi 3B+ (1 GB RAM)
- **Recomendado:** Raspberry Pi 4 o superior (≥2 GB RAM) para mejor rendimiento de IA y sin limitaciones gráficas
- **Pendiente de testing:** Raspberry Pi 2, 3A, Zero 2W, 5

> [!IMPORTANT]
> Con Raspberry Pi anterior a la versión 4, **Organic Maps** funcionará mediante renderizado por software (automático). La experiencia puede ser más lenta, pero es funcional.

### Soporte de Almacenamiento

La elección del almacenamiento es crítica en Raspberry Pi, ya que las tarjetas microSD baratas se degradan rápidamente bajo el uso constante de un sistema operativo:

*   **Recomendación de Oro:** Un **SSD con adaptador USB** o un **SSD montado en HAT NVMe** dará la mejor experiencia. Las tarjetas microSD baratas se desgastan en pocos meses de uso intensivo.
*   **Capacidad:**
    *   **16 GB (Mínimo):** Sistema base + WikiMed + IA mínima. Sin espacio para Wikipedia.
    *   **32 GB (Equilibrado):** Todo lo anterior + Wikipedia Ligera.
    *   **64 GB (Estándar):** El punto ideal. Incluye Wikipedia completa (texto) y modelo IA básico.
    *   **128 GB o más:** Permite WikiHow, Wikipedia con imágenes y múltiples modelos de IA.

> [!TIP]
> Usa siempre una **tarjeta microSD de Clase A2** (ej: SanDisk Extreme, Samsung Pro Endurance) si no tienes SSD. Son las únicas diseñadas para soportar el uso aleatorio de lectura/escritura de un sistema operativo de forma continuada.

---

## 2. Instalación del Sistema Operativo Base

### Paso 1: Raspberry Pi Imager (Obligatorio)

La forma oficial y más sencilla de instalar Raspberry Pi OS es usando la herramienta oficial **Raspberry Pi Imager**:

👉 **[Guía oficial de Raspberry Pi Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager)**

1.  Descarga e instala **Raspberry Pi Imager** en tu PC (Windows, Mac o Linux).
2.  Conecta tu tarjeta microSD o SSD USB a tu PC.
3.  En Imager, selecciona:
    *   **Dispositivo:** Tu modelo de Raspberry Pi
    *   **Sistema Operativo:** `Raspberry Pi OS (64-bit)` — la versión de escritorio completa con entorno gráfico
    *   **Almacenamiento:** Tu tarjeta/SSD
4.  Haz clic en **Siguiente** y configura las opciones personalizadas:
    *   Nombre de host, usuario y contraseña
    *   Tu red WiFi (si la usas)
    *   Habilitar SSH si lo necesitas
5.  Confirma y espera a que termine la escritura.

> [!TIP]
> Si quieres usar una red WiFi, es mucho más cómodo configurarla desde Imager antes de grabar que hacerlo después desde la propia Raspberry Pi.

### Paso 2: Primer arranque

1.  Inserta la tarjeta/SSD en la Raspberry Pi y enciéndela.
2.  El sistema arrancará directamente al escritorio (si usaste la edición de escritorio).
3.  Configura el idioma y teclado si el asistente de bienvenida lo solicita.

---

## 3. Instalación de refugiOS

Una vez dentro del escritorio de Raspberry Pi OS, abre una terminal y ejecuta:

```bash
sudo apt install curl -y
curl -fsSL https://raw.githubusercontent.com/Ganso/refugiOS/main/install.sh | bash
```

El instalador detectará automáticamente la arquitectura ARM y adaptará todas las decisiones:
- Usará `kiwix` via APT en lugar de AppImage (x86 only)
- Configurará Organic Maps para renderizado por software si es una RPi anterior a la versión 4
- Ajustará la selección por defecto de módulos según la RAM y el espacio disponibles

---

## 4. Diferencias respecto a la instalación en XUbuntu

| Característica | Raspberry Pi | XUbuntu |
| :--- | :--- | :--- |
| **Kiwix Desktop** | APT (`kiwix`) | AppImage o Flatpak |
| **Organic Maps** | Software rendering en RPi <4, GPU nativa en RPi 4+ | GPU nativa |
| **Bóvedas criptográficas** | ✅ Funcional | ✅ Funcional |
| **Asistente IA** | ⚠ Limitado por RAM (recomendado modelo mínimo en 3B+) | ✅ Completo |
| **Gestor de ventanas** | Wayfire / Labwc (Wayland) | XFCE (X11 o Wayland) |

---

## 5. Configuración del teclado en español

Si el sistema arrancó en inglés y necesitas el teclado en español:

1.  Haz clic en el menú de aplicaciones.
2.  Ve a **Preferencias** → **Raspberry Pi Configuration** → pestaña **Localisation**.
3.  Configura **Locale**, **Keyboard** y **Timezone** según tu país.
4.  Reinicia cuando se solicite.

---

## 6. Notas sobre rendimiento

*   **Memoria RAM:** Con solo 1 GB (Raspberry Pi 3B+), se recomienda el modelo de IA mínimo (Qwen2.5-0.5B). El modelo básico (Phi-4-mini) puede funcionar pero con swap activo y lentitud notable.
*   **Swap:** Para usar modelos de IA más grandes, puedes ampliar el swap:
    ```bash
    sudo dphys-swapfile swapoff
    sudo nano /etc/dphys-swapfile  # Cambia CONF_SWAPSIZE=100 por 2048
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    ```
*   **Kiwix:** Funciona correctamente. Necesita unos segundos adicionales de indexación la primera vez que abre una enciclopedia grande.

---

## 7. Conocimiento Offline (ZIM)

El proceso de descarga e instalación de bases de conocimiento (Wikipedia, WikiMed, WikiHow) es idéntico al de XUbuntu. Consulta la [Guía de instalación en XUbuntu](instalacion_xubuntu.md) para los detalles de selección de contenidos.

Al finalizar, tu Raspberry Pi ejecutará **refugiOS** de forma **totalmente autónoma**, sin Internet, con conocimiento enciclopédico, mapas offline e inteligencia artificial local.
