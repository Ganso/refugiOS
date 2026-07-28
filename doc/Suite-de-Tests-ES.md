# Suite de Tests Automáticos de refugiOS

Esta guía describe la comprobación automática del proyecto: qué cubre, cómo ejecutarla y cómo ampliarla. Está pensada para quien **desarrolla o modifica refugiOS**; si solo vas a usar el sistema, no necesitas nada de esto.

La suite vive en la carpeta [`tests/`](https://github.com/Ganso/refugiOS/tree/main/tests) del repositorio y cubre los tres momentos distintos del sistema: la **construcción** de la imagen, la **instalación** de módulos y la **ejecución** en el dispositivo del usuario.

Dos ideas guían todo el diseño:

1. **Nada requiere `sudo` en tu máquina.** Lo que necesita root de verdad (`debootstrap`, dispositivos loop, `cryptsetup`) se ejecuta dentro de un contenedor Debian privilegiado.
2. **Un test que no falla sin la corrección no sirve.** Cada comprobación se validó también contra el código anterior al arreglo, en una copia aparte del repositorio.

> [!NOTE]
> El proyecto **no tiene integración continua**: nada ejecuta la suite automáticamente. Ejecútala tú antes de proponer un cambio.

---

## 1. Uso rápido

```bash
bash tests/run_all.sh
```

Ejecuta la suite entera (unos 3-4 minutos, la primera vez algo más porque construye la imagen de Docker). Devuelve código 0 si todo está correcto.

Si no quieres usar Docker o solo buscas una comprobación inmediata:

```bash
bash tests/run_all.sh --quick
```

Ejecuta únicamente lo que corre en tu máquina: sintaxis y los tests de los scripts Bash.

---

## 2. Requisitos

| Herramienta | Para qué | Obligatoria |
| :--- | :--- | :--- |
| `docker` (con tu usuario en el grupo `docker`) | Contenedor privilegiado para lo que requiere root | Sí, salvo con `--quick` |
| `qemu-system-x86_64` + `/dev/kvm` | Arrancar imágenes construidas | Solo para las pruebas de arranque |
| paquete `ovmf` | Firmware UEFI para QEMU | Solo para las pruebas de arranque |
| `imagemagick` (`convert`) | Convertir las capturas de QEMU a PNG | Solo para las pruebas de arranque |
| Conexión a Internet | Un caso de `test_install_sh.sh` y el `debootstrap` de `test_build.sh` | Recomendable |

Comprobación rápida de que tienes lo necesario:

```bash
docker info >/dev/null && test -w /dev/kvm && ls /usr/share/OVMF/OVMF_CODE*.fd && command -v convert
```

---

## 3. Qué hay en cada fichero

### 3.1. Ejecución

| Fichero | Qué hace |
| :--- | :--- |
| `run_all.sh` | Lanza la suite completa. Con `--quick`, solo lo que no necesita contenedor. |
| `run_in_container.sh` | Envoltorio: ejecuta un comando dentro del contenedor privilegiado con el repositorio montado en `/repo`. |
| `docker/Dockerfile` | Contenedor Debian Trixie con `debootstrap`, `cryptsetup`, `parted`, `aria2`, `shellcheck`… |

### 3.2. Comprobaciones

| Fichero | Qué comprueba | Necesita contenedor |
| :--- | :--- | :--- |
| `lint.sh` | Sintaxis de los 8 scripts Bash (`bash -n`) y los 3 Python (`py_compile`). Con `shellcheck` disponible, informa del número de avisos por fichero (no bloquea). | No |
| `unit_bash.sh` | Precedencia de idioma en `i18n.sh`, selección de versión en `refugios-kiwix.sh`, el ciclo completo de `refugios-ai-selector.sh` y el paso de argumentos y cálculo de RAM de `test_boot.sh`. | No |
| `unit_install.py` | Funciones internas de `install.py`: reanudación de descargas, timeouts, orden de versiones, saneado de textos para `dialog`, código de salida, prioridad de los scripts locales y claves de traducción sin traducir. | Sí (usa `aria2c`) |
| `test_install_sh.sh` | El bootstrapper `install.sh`: que el modo desarrollador tenga efecto, que el modo normal descargue de GitHub, y las validaciones de `i18n.py` y de terminal ausente. | Sí |
| `test_vault.sh` | Creación real de bóvedas LUKS: contraseñas distintas rechazadas, contraseñas iguales aceptadas, y ciclo abrir → escribir → cerrar → reabrir. | Sí (root real) |
| `test_build.sh` | Construcción real de imagen, abortada a propósito nada más entrar en el chroot: que el fallo detenga el build, que la imagen previa se descarte y que no queden montajes apilados. | Sí (root real) |

### 3.3. Utilidades

| Fichero | Para qué |
| :--- | :--- |
| `luks_pty.py` | Ejecuta `cryptsetup luksFormat` sobre un terminal real y responde a sus prompts. Hace falta porque cryptsetup se niega a verificar la contraseña si la entrada es una tubería. |
| `qemu_boot_check.py` | Arranca una imagen sin interfaz gráfica y toma capturas de pantalla en los instantes que le indiques. |
| `qemu_ctl.py` | Controla una máquina virtual ya arrancada: capturas, teclas, texto y clics de ratón. |
| `prepare_e2e_image.sh` | Prepara una copia de una imagen construida para probar el instalador de principio a fin: le inyecta el repositorio local y lanza el instalador al iniciar sesión. |

---

## 4. Ejecutar comprobaciones sueltas

Cada test funciona por separado. Los que necesitan root van por el envoltorio:

```bash
bash tests/lint.sh
```

```bash
bash tests/unit_bash.sh
```

```bash
bash tests/run_in_container.sh python3 -W ignore tests/unit_install.py
```

```bash
bash tests/run_in_container.sh bash tests/test_install_sh.sh
```

```bash
bash tests/run_in_container.sh bash tests/test_vault.sh
```

```bash
bash tests/run_in_container.sh bash tests/test_build.sh
```

Para un único caso de los tests de Python:

```bash
bash tests/run_in_container.sh python3 -W ignore tests/unit_install.py TestDownloadResume
```

Y para abrir una consola dentro del contenedor y trastear a mano:

```bash
bash tests/run_in_container.sh bash
```

---

## 5. Pruebas de imagen y arranque

Estas no forman parte de `run_all.sh` porque tardan entre 20 y 40 minutos.

### 5.1. Construir una imagen sin usar sudo

```bash
mkdir -p ~/refugios-builds && docker run --rm --privileged -v "$PWD:/repo" -v ~/refugios-builds:/out -v /dev:/dev -w /out refugios-test:trixie /repo/scripts/build_refugios.sh -s 12G -l es
```

La imagen queda como `root`; para poder arrancarla con QEMU, devuélvela a tu usuario:

```bash
docker run --rm -v ~/refugios-builds:/out refugios-test:trixie chown -R 1000:1000 /out
```

### 5.2. Verificar que arranca

```bash
python3 tests/qemu_boot_check.py ~/refugios-builds/refugios-base-12G-es.img --shots 25,60,100 --out tests/out --prefix mi_imagen
```

Deja los PNG en `tests/out/`. Ábrelos y comprueba la secuencia esperada: GRUB, inicio de sesión automático, escritorio XFCE y el mensaje de bienvenida con el tamaño real del disco.

Opciones útiles:

- `--net none` arranca sin red — es la prueba de que el sistema funciona sin conexión.
- `--ram 4` fija la memoria de la máquina virtual en GiB.
- `--size 1920x1080` fija la resolución de la pantalla virtual.
- `--keep` deja la máquina viva al terminar, para poder controlarla (ver más abajo).

### 5.3. Probar el instalador de principio a fin

Prepara una copia de la imagen con el repositorio local inyectado, de modo que el instalador use **tu código** y no el publicado en GitHub:

```bash
docker run --rm --privileged -v "$PWD:/repo" -v ~/refugios-builds:/out -v /dev:/dev -w /repo -e REFUGIOS_IN_CONTAINER=1 refugios-test:trixie bash tests/prepare_e2e_image.sh /out/refugios-base-12G-es.img /out/e2e.img
```

Arranca la copia dejándola viva:

```bash
python3 tests/qemu_boot_check.py ~/refugios-builds/e2e.img --shots 60 --out tests/out --prefix e2e --keep
```

El instalador se abre solo al iniciar sesión. A partir de ahí se conduce con `qemu_ctl.py`, que habla con la máquina por el socket que ha quedado en `tests/out/e2e_qmp.sock`:

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock shot paso1
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock key ret
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock key down spc ret
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock text "mi_boveda"
```

```bash
python3 tests/qemu_ctl.py tests/out/e2e_qmp.sock dblclick 65 490
```

Nombres de teclas: `ret`, `tab`, `spc`, `esc`, `up`, `down`, `left`, `right`, `backspace`, y combinaciones con guion (`ctrl-c`, `alt-f4`, `shift-a`).

Para detener la máquina cuando termines:

```bash
kill $(cat tests/out/e2e_qemu.pid)
```

> [!WARNING]
> **Aviso sobre el teclado:** la imagen en español usa distribución `es`, así que al usar `text` los caracteres `-`, `;` y `=` salen como `'`, `ñ` y `¡`. Escribe órdenes que solo lleven letras, números y espacios, o envía esos símbolos con `key`.

---

## 6. Añadir un test nuevo

1. Decide dónde encaja: comportamiento de un script Bash → `unit_bash.sh`; función interna de `install.py` → `unit_install.py`; algo que necesite root de verdad → un `test_*.sh` que se lance con `run_in_container.sh`.
2. Los tests en Bash usan la función `check`, que recibe un código de salida y una descripción: `check $? "descripción de lo que debería pasar"`.
3. Para los scripts que llaman a programas externos, crea dobles en un directorio temporal y ponlo primero en el `PATH` — así lo hace `unit_bash.sh` con `dialog`, `curl`, `llamafile` y `qemu-system-x86_64`.
4. **Comprueba que el test falla sin la corrección.** Vuelca la versión anterior del fichero en un directorio aparte y ejecuta el test contra ella:

```bash
mkdir -p /tmp/orig/scripts && git show main:scripts/refugios-kiwix.sh > /tmp/orig/scripts/refugios-kiwix.sh
```

---

## 7. Cuando algo parece colgado

- **`cryptsetup` tarda muchísimo.** Con los parámetros por defecto (argon2id, 1 GiB de memoria) cada operación lleva minutos dentro de un contenedor. `test_vault.sh` abarata el KDF *solo para el test*, manteniendo intactas las opciones que se están probando.
- **Un contenedor huérfano de una ejecución anterior** bloquea a `cryptsetup` y a los dispositivos loop. Mira `docker ps` antes de investigar nada más.
- **`expect`.** Se probó y se descartó: con la forma de bloque y con `expect_before timeout` dejaba de emparejar los prompts y el test se quedaba colgado sin explicación. Por eso el control del terminal está en `luks_pty.py`, que es explícito y se puede leer entero.
- **QEMU no arranca la imagen** con «Permission denied»: la imagen pertenece a `root` porque la construyó el contenedor. Devuélvela a tu usuario con el `chown` de más arriba.

---

## 8. Qué no cubren estos tests

No hay comprobación automática de la instalación completa de módulos grandes (Wikipedia total, mapas), ni del comportamiento en Raspberry Pi, ni del arranque en hardware real por BIOS heredada. Todo eso sigue siendo manual.

---

## Enlaces relacionados

- **[Guía de Construcción de Imagen de Sistema](Construccion-Imagen-Sistema-ES.md)** — cómo se genera la imagen que estos tests verifican.
- **[Guía de Virtualización](Guia-Virtualizacion-y-Pendrive-ES.md)** — arrancar imágenes en QEMU o VirtualBox de forma manual.
- **[Arquitectura del Sistema](Arquitectura-ES.md)** — qué hace cada script del proyecto.
