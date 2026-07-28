<h1 align="center">refugiOS — Capturas de pantalla / Screenshots</h1>

<p align="center">
  <a href="../README.md"><strong>← Volver a Media / Back to Media</strong></a>
</p>

---

## 🇪🇸 Español

Cuarenta capturas de refugiOS en funcionamiento, veinte en español y veinte en inglés,
tomadas sobre el sistema real arrancado en una máquina virtual a 1920×1080. Recorren la
instalación completa y cada una de las aplicaciones principales.

Las capturas son documentación adicional: no se enlazan desde las guías del proyecto.

### Cómo se han obtenido

Se construyeron dos imágenes base (una por idioma), se ejecutó el instalador completo
seleccionando Wikipedia ligera, cartografía y el modelo de IA mínimo, y se abrió cada
aplicación. Todo el recorrido se hizo con las herramientas de la
**[Suite de Tests Automáticos](../../doc/Suite-de-Tests-ES.md)**: `qemu_boot_check.py`
para arrancar y `qemu_ctl.py` para navegar y capturar.

> [!NOTE]
> Las respuestas de la IA se generaron con el modelo **mínimo (Qwen3-0.6B, ~380 MB)**, que
> es el más pequeño de los cinco disponibles. Su calidad no representa la de los modelos
> mayores; está ahí para mostrar la interfaz funcionando sin conexión.

### Índice

| # | Qué muestra | 🇪🇸 Español | 🇬🇧🇺🇸 English |
| :--- | :--- | :--- | :--- |
| 01 | Mensaje de bienvenida del primer arranque, con el tamaño real del dispositivo. | [es/01_bienvenida.png](es/01_bienvenida.png) | [en/01_welcome.png](en/01_welcome.png) |
| 02 | Instalador: elección de idioma, preseleccionado según el sistema. | [es/02_instalador_idioma.png](es/02_instalador_idioma.png) | [en/02_installer_language.png](en/02_installer_language.png) |
| 03 | Instalador: diagnóstico del equipo (RAM, disco, GPU) que condiciona las opciones ofrecidas. | [es/03_instalador_diagnostico.png](es/03_instalador_diagnostico.png) | [en/03_installer_diagnostics.png](en/03_installer_diagnostics.png) |
| 04 | Instalador: elección de la edición de Wikipedia, de 73 MB a 38 GB. | [es/04_instalador_wikipedia.png](es/04_instalador_wikipedia.png) | [en/04_installer_wikipedia.png](en/04_installer_wikipedia.png) |
| 05 | Instalador: bases de conocimiento adicionales (WikiMed, WikiHow). | [es/05_instalador_otras_wikis.png](es/05_instalador_otras_wikis.png) | [en/05_installer_other_wikis.png](en/05_installer_other_wikis.png) |
| 06 | Instalador: módulo de cartografía offline con Organic Maps. | [es/06_instalador_mapas.png](es/06_instalador_mapas.png) | [en/06_installer_maps.png](en/06_installer_maps.png) |
| 07 | Instalador: modelos de IA local, con el aviso de RAM necesaria para cada uno. | [es/07_instalador_ia.png](es/07_instalador_ia.png) | [en/07_installer_ai.png](en/07_installer_ai.png) |
| 08 | Instalador: confirmación final con el espacio estimado. | [es/08_instalador_confirmacion.png](es/08_instalador_confirmacion.png) | [en/08_installer_confirmation.png](en/08_installer_confirmation.png) |
| 09 | Instalador: resumen al terminar, con el espacio realmente ocupado. | [es/09_instalador_completado.png](es/09_instalador_completado.png) | [en/09_installer_finished.png](en/09_installer_finished.png) |
| 10 | Escritorio tras la instalación, con los lanzadores de todos los módulos. | [es/10_escritorio.png](es/10_escritorio.png) | [en/10_desktop.png](en/10_desktop.png) |
| 11 | Wikipedia offline en Kiwix: portada de la edición instalada. | [es/11_wikipedia_kiwix.png](es/11_wikipedia_kiwix.png) | [en/11_wikipedia_kiwix.png](en/11_wikipedia_kiwix.png) |
| 12 | Wikipedia offline: un artículo completo, sin conexión a Internet. | [es/12_wikipedia_articulo.png](es/12_wikipedia_articulo.png) | [en/12_wikipedia_article.png](en/12_wikipedia_article.png) |
| 13 | Organic Maps: mapamundi vectorial listo para descargar regiones. | [es/13_mapas_mundo.png](es/13_mapas_mundo.png) | [en/13_maps_world.png](en/13_maps_world.png) |
| 14 | Organic Maps: detalle con carreteras y topónimos en el idioma del sistema. | [es/14_mapas_detalle.png](es/14_mapas_detalle.png) | [en/14_maps_detail.png](en/14_maps_detail.png) |
| 15 | Selector de IA local: muestra la RAM utilizable y qué modelos caben. | [es/15_ia_selector.png](es/15_ia_selector.png) | [en/15_ai_selector.png](en/15_ai_selector.png) |
| 16 | IA local respondiendo sin conexión, con el recuento de tokens y la velocidad. | [es/16_ia_chat.png](es/16_ia_chat.png) | [en/16_ai_chat.png](en/16_ai_chat.png) |
| 17 | Gestor de bóvedas cifradas: menú principal. | [es/17_bovedas_menu.png](es/17_bovedas_menu.png) | [en/17_vaults_menu.png](en/17_vaults_menu.png) |
| 18 | Creación de una bóveda LUKS: la contraseña se pide dos veces para evitar erratas irreversibles. | [es/18_bovedas_creacion.png](es/18_bovedas_creacion.png) | [en/18_vault_creation.png](en/18_vault_creation.png) |
| 19 | Gestor de bóvedas con una bóveda ya creada, su estado y su tamaño. | [es/19_bovedas_lista.png](es/19_bovedas_lista.png) | [en/19_vaults_list.png](en/19_vaults_list.png) |
| 20 | Bóveda abierta: aparece montada en el escritorio como una carpeta normal. | [es/20_boveda_abierta.png](es/20_boveda_abierta.png) | [en/20_vault_open.png](en/20_vault_open.png) |

---

## 🇬🇧🇺🇸 English

Forty screenshots of refugiOS in use, twenty in Spanish and twenty in English, taken on the
real system booted in a virtual machine at 1920×1080. They walk through the full
installation and each of the main applications.

The screenshots are additional documentation: they are not linked from the project guides.

### How they were produced

Two base images were built (one per language), the full installer was run selecting the
light Wikipedia, cartography and the minimal AI model, and each application was opened.
The whole walkthrough was driven with the tools of the
**[Automated Test Suite](../../doc/Test-Suite-EN.md)**: `qemu_boot_check.py` to boot and
`qemu_ctl.py` to navigate and capture.

> [!NOTE]
> The AI answers were generated with the **minimal model (Qwen3-0.6B, ~380 MB)**, the
> smallest of the five available. Its quality does not represent that of the larger models;
> it is there to show the interface working offline.

### Index

| # | What it shows | 🇪🇸 Spanish | 🇬🇧🇺🇸 English |
| :--- | :--- | :--- | :--- |
| 01 | First-boot welcome message, showing the real device size. | [es/01_bienvenida.png](es/01_bienvenida.png) | [en/01_welcome.png](en/01_welcome.png) |
| 02 | Installer: language choice, preselected from the system. | [es/02_instalador_idioma.png](es/02_instalador_idioma.png) | [en/02_installer_language.png](en/02_installer_language.png) |
| 03 | Installer: hardware diagnosis (RAM, disk, GPU) that shapes the options offered. | [es/03_instalador_diagnostico.png](es/03_instalador_diagnostico.png) | [en/03_installer_diagnostics.png](en/03_installer_diagnostics.png) |
| 04 | Installer: choice of Wikipedia edition, from 73 MB to 38 GB. | [es/04_instalador_wikipedia.png](es/04_instalador_wikipedia.png) | [en/04_installer_wikipedia.png](en/04_installer_wikipedia.png) |
| 05 | Installer: additional knowledge bases (WikiMed, WikiHow). | [es/05_instalador_otras_wikis.png](es/05_instalador_otras_wikis.png) | [en/05_installer_other_wikis.png](en/05_installer_other_wikis.png) |
| 06 | Installer: offline cartography module with Organic Maps. | [es/06_instalador_mapas.png](es/06_instalador_mapas.png) | [en/06_installer_maps.png](en/06_installer_maps.png) |
| 07 | Installer: local AI models, each with its RAM requirement. | [es/07_instalador_ia.png](es/07_instalador_ia.png) | [en/07_installer_ai.png](en/07_installer_ai.png) |
| 08 | Installer: final confirmation with the estimated space. | [es/08_instalador_confirmacion.png](es/08_instalador_confirmacion.png) | [en/08_installer_confirmation.png](en/08_installer_confirmation.png) |
| 09 | Installer: summary on completion, with the space actually used. | [es/09_instalador_completado.png](es/09_instalador_completado.png) | [en/09_installer_finished.png](en/09_installer_finished.png) |
| 10 | Desktop after installation, with the launchers for every module. | [es/10_escritorio.png](es/10_escritorio.png) | [en/10_desktop.png](en/10_desktop.png) |
| 11 | Offline Wikipedia in Kiwix: front page of the installed edition. | [es/11_wikipedia_kiwix.png](es/11_wikipedia_kiwix.png) | [en/11_wikipedia_kiwix.png](en/11_wikipedia_kiwix.png) |
| 12 | Offline Wikipedia: a full article, with no Internet connection. | [es/12_wikipedia_articulo.png](es/12_wikipedia_articulo.png) | [en/12_wikipedia_article.png](en/12_wikipedia_article.png) |
| 13 | Organic Maps: vector world map, ready to download regions. | [es/13_mapas_mundo.png](es/13_mapas_mundo.png) | [en/13_maps_world.png](en/13_maps_world.png) |
| 14 | Organic Maps: detail with roads and place names in the system language. | [es/14_mapas_detalle.png](es/14_mapas_detalle.png) | [en/14_maps_detail.png](en/14_maps_detail.png) |
| 15 | Local AI selector: shows usable RAM and which models fit. | [es/15_ia_selector.png](es/15_ia_selector.png) | [en/15_ai_selector.png](en/15_ai_selector.png) |
| 16 | Local AI answering offline, with token count and speed. | [es/16_ia_chat.png](es/16_ia_chat.png) | [en/16_ai_chat.png](en/16_ai_chat.png) |
| 17 | Encrypted vault manager: main menu. | [es/17_bovedas_menu.png](es/17_bovedas_menu.png) | [en/17_vaults_menu.png](en/17_vaults_menu.png) |
| 18 | Creating a LUKS vault: the password is asked twice to prevent an irreversible typo. | [es/18_bovedas_creacion.png](es/18_bovedas_creacion.png) | [en/18_vault_creation.png](en/18_vault_creation.png) |
| 19 | Vault manager with a vault already created, its state and size. | [es/19_bovedas_lista.png](es/19_bovedas_lista.png) | [en/19_vaults_list.png](en/19_vaults_list.png) |
| 20 | Vault opened: it appears mounted on the desktop as an ordinary folder. | [es/20_boveda_abierta.png](es/20_boveda_abierta.png) | [en/20_vault_open.png](en/20_vault_open.png) |

---

## Licencia / License

Forman parte del proyecto refugiOS y se distribuyen bajo la licencia
[AGPL-3.0](../../LICENSE). El logotipo que aparece en el fondo de escritorio es obra de
**[Felipe Monge "PlayOnRetro"](https://x.com/PlayOnRetro)**.

They are part of the refugiOS project and are distributed under the
[AGPL-3.0](../../LICENSE) license. The logo shown in the desktop wallpaper is the work of
**[Felipe Monge "PlayOnRetro"](https://x.com/PlayOnRetro)**.
