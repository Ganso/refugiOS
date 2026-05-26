# Tabla de Compatibilidad

En este documento se detalla el estado de compatibilidad de **refugiOS** con diferentes sistemas operativos y arquitecturas de hardware.

## Arquitectura x86 (PC / Laptop)

| Sistema Operativo | Estado | Notas |
| :--- | :--- | :--- |
| **XUbuntu 24.04 LTS** | ✅ Certificado | Plataforma de referencia y recomendada |
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

La imagen base generada por `scripts/build_refugios.sh` tiene un problema conocido:

*   **Iconos del escritorio no marcados como fiables:** Los lanzadores `.desktop` del escritorio no se marcan correctamente como fiables por XFCE. Al hacer doble clic, XFCE muestra un diálogo de advertencia pidiendo confirmación antes de ejecutar la aplicación. El mecanismo de confianza inyectado (checksum SHA-256 vía GIO `metadata::xfce-exe-checksum`) no es reconocido por XFCE. Solución temporal: clic derecho sobre el icono → "Permitir lanzamiento". Ver detalles en la **[Guía de Construcción de Imagen de Sistema](Construccion-Imagen-Sistema-ES#7-bug-conocido-iconos-del-escritorio-no-marcados-como-fiables)**.

---
[Volver al README](../README.md)
