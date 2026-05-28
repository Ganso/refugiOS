# Tabla de Compatibilidad

En este documento se detalla el estado de compatibilidad de **refugiOS** con diferentes sistemas operativos y arquitecturas de hardware.

> [!TIP]
> La **imagen pregenerada** de refugiOS (descargable desde [refugios.ganso.org](https://refugios.ganso.org/)) está basada en Debian Trixie con XFCE y es la forma más sencilla de empezar en PC. No requiere instalación previa del sistema operativo base.

## Arquitectura x86 (PC / Laptop)

| Sistema Operativo / Método | Estado | Notas |
| :--- | :--- | :--- |
| **Imagen pregenerada (Debian Trixie)** | ✅ Certificado | Método recomendado. Descarga directa desde [refugios.ganso.org](https://refugios.ganso.org/) |
| **XUbuntu 24.04 LTS** | ✅ Certificado | Método alternativo (Live con persistencia) |
| **Xubuntu 25.10** | ✅ Certificado | Necesario retestear cada nueva release |
| **Debian 11 (Bullseye)**| ⚠️ Con problemas | Requiere ajustes. Ver [Detalles Técnicos](#debian-11-bullseye) |
| **Otras distros (Debian/Ubuntu)** | 🧪 Sin testar | Se buscan testers |

## Arquitectura ARM (Raspberry Pi)

| Dispositivo | Estado | Versión Raspberry OS | Notas |
| :--- | :--- | :--- | :--- |
| **Raspberry Pi 3B+** | ✅ Certificado | 13 de abril de 2026 | Recomendado (RPi OS 64-bit) |
| **Raspberry Pi 4 / 5** | 🧪 Sin testar | - | Teóricamente funcional |
| **Raspberry Pi Zero 2W** | 🧪 Sin testar | - | Se buscan testers |

---

## 🧪 Detalle de Pruebas y Problemas Conocidos

### Debian 11 (Bullseye)
Se ha probado la instalación en Debian 11, pero se han identificado varios problemas que requieren intervención manual o corrección futura:

*   **Flatpak:** Es posible que el paquete de Flatpak no se instale automáticamente durante el proceso de configuración inicial.
*   **AppImages:** Se han reportado errores con las dependencias necesarias para ejecutar algunas AppImages. 
*   **Seguimiento de errores:** Estos fallos están siendo seguidos en el **[Bug #10](https://github.com/Ganso/refugiOS/issues/10)** de la distribución.

### Imagen Nativa de Sistema (build_refugios.sh)

La imagen base generada por `scripts/build_refugios.sh` no requiere pasos manuales posteriores para los iconos del escritorio. Los lanzadores se marcan automáticamente como fiables por XFCE en el primer inicio de sesión mediante el mecanismo de metadatos GIO `metadata::xfce-exe-checksum` (requiere `libglib2.0-bin`, incluido en la imagen).

---
[Volver al README](../README.md)
