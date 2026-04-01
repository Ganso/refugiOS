# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto se rige por [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.03] - 2026-04-02

### Añadido
- **Soporte Hardware**: Pruebas preliminares en **Raspberry Pi 3B+**. El script de instalación es funcional tras resolver dependencias críticas, aunque con limitaciones importantes de arquitectura y rendimiento.

### Cambiado
- **Instalador**: Eliminada la dependencia obligatoria de `language-selector-common` para mejorar la compatibilidad con Raspberry Pi OS (Debian).
- **Instalador**: Dividida la instalación de paquetes en bloques de máximo 5 unidades para evitar errores por falta de memoria (OOM) en dispositivos con poca RAM.
- **Instalador**: Oculta la "Advertencia de Persistencia" cuando se detecta hardware Raspberry Pi.
- **Escritorio**: Configuración automática de `pcmanfm` para evitar el diálogo de confirmación al ejecutar lanzadores.

### Errores conocidos (Raspberry Pi)
- **Kiwix**: No funcional. Requiere una versión de Kiwix Desktop compilada para arquitectura ARM (actualmente descarga x86_64).
- **Organic Maps**: No funcional por errores en la inicialización de OpenGL ES3/Framebuffer. Pendiente de optimización de drivers/entorno.
- **Inteligencia Artificial**: Modelos como Phi-4-mini no han podido ser validados satisfactoriamente debido a las severas limitaciones de RAM (1GB) de la Raspberry Pi 3B+.

## [0.02] - 2026-04-01

### Añadido
- **Instalador**: Opción para omitir la descarga de Wikipedia (grande o pequeña) en `install.sh`.
- **Documentación**: Sección en "Módulos de Software" sobre la futura migración del instalador a Python para mejorar su mantenimiento, así como otras mejoras propuestas.

### Cambiado
- **Instalador**: Lógica de descarga ZIM optimizada para ser totalmente condicional y limpiar enlaces simbólicos previos si se omiten módulos. Mejoras en el sistema de menús.
