# Guía Técnica de Ensamblaje Manual (Proof-of-Concept)

Mientras este desarrollo transcurre sus ciclos alfa, es imperativo erigir la Proof Of Concept "a mano". Esto valida la viabilidad de todos los subsistemas lógicos y el funcionamiento interno de Linux. 
Los siguientes pasos detallan minuciosamente cómo se edifica de manera quirúrgica un refugio completo.  *(Se asume un nivel experto-intermedio en interacciones con sistemas operativos basados en distribuciones Debian CLI)*.

## 1. Selección de la Imagen de Software Base

La aleación tecnológica idónea proviene de los clústeres de origen Canonical bajo factor de miniaturización optimizado: **Xubuntu 24.04 LTS Minimal** (o alternativamente **Xubuntu 25.10 Minimal**).
Es de estricta obligatoriedad priorizar ramas nominales *"Minimal"* (Imágenes de alrededor de ~1.5 - 2 GB, contrapuestas a su variante general de mas de ~3.5 GB). Las compilaciones menores desinstalan de base paquetes de utilería ofimática prescindible como hojas lúdicas o utilidades redundantes permitiendo amasar y recuperar gygabytes estelares para datos y persistencia.

## 2. Estrategias Matemáticas de Hardware Físico (Capacidad del Pendrive)

Cada escalón de densidad altera la táctica de acopio al límite. 

*   **Escudo Extremo [16 GB] (Mínimo Absoluto):** Escenario de pobreza computacional crítico. Espacio suficiente única y exlusivamente de instalar: Entorno Minimal Base SO (~2GB), la enciclopedia clínica **WikiMed** (~2 GB), Cartografías primordiales liminares del usuario en el programa **Organic Maps** (~1 GB), red modular inteligente ultraligera basada en deducción combinatoria inferior **DeepSeek R1 de 1.5B en SLM** (~1.1 GB). Contenedor o Bóveda LUKS marginal con escasos megabytes. Relevando la masiva obra de Wikipedia a la exclusión eterna del USB por limitación de bloque.
*   **Armazón Táctico Boreal [32 GB]:** Integra íntegramente todo el sector superior, con la salvedad de incrustarse en los pliegos las infraestructuras modulares reducidas de conocimiento literario como las Wikipédicas de la facción "Mini" o Wikipedia en vertiente puramente textual sin acompañamiento icónico (Ej: Variante `_nopic.zim`). Elevaciones medias extendiendo la Bóveda de archivos vital a (~5 GB absolutos).
*   **Armadura de Prepper Estándar [64 GB]:** El eje vertebrador nominal del proyecto. Balance simétrico entre resiliencia y base pesada. Almacena las variables anteriores además del portador magistral: La **Wikipedia Universal Hispana Máxima con fotografías incorporadas integramente** (~40GB-45GB ajustables a volatilidad temporal). Expandiendo el SLM a **Phi-3.5 Mini SLM** de razonamiento lógico robusto en veintenas de idiomas (~2.6-4 GB), mapas a escalas semi-continentales en alta granularidad y la Bóveda operativa (~5.5-10 GB).
*   **El Repositorio de Alejandría [≥128 GB]:** Elimina la necesidad de particionamiento heurístico. Absorbe en sí mismola matriz original conmutada del **Survivor Library Tecnológica de la Ingeniería Preindustrial Completa (~250 GB usando un disco de 512GB NMVe)**, o absorciones planetarias del Organic Maps, o la mismísima matriz generalista de la Wikipedia Anglosajona Máxima Master de >115 GB.

---

## 3. Arquitecturas De Formato: "Live USB Persistente" versus "Full Native Install"

Para materializarse en un equipo externo, el SO admite ser desplegado en bifurcaciones sistémicas excluyentes por tecnología e intencionalidad técnica:

### Opción A: Entorno "Live USB" con extensión de Memoria Persistente (Aconsejable/Agnóstica)
Bajo esta modalidad el sistema central de Xubuntu sigue atrincherado residiendo de manera segura en un macro-archivo imagen prezippeado de matriz inerte y blindada *Read-Only*. Pero el instalador del disco de rescate acopia bajo el resto del pendrive una sub-unión de almacenamiento con memoria "escribible".
*   **Fortalezas Fundamentales:** Preserva sobremneramente la micro-trazabilidad electrónica natural de bloques (Reads-Writes). Las micro SD o tarjetas USB simples soportan pésimamente un kernel ext4 completo de Linux actualizando crónicas con journaling por cada nanosegundo. Un Live USB amaina este fenómeno impidiendo un borrado/muerte NAND precipitado (Brick) extendiendo por décadas su viabilidad almacenada impoluta. Por añadidura erradica por completo la injerencia o intrusismo accidental a nivel de particionario base del Host original.
*   **Contraindicaciones:** Ralentización de segundos en ruteo boot-loading por descompresión on-fly temporal del Root.

### Opción B: "Full Native Install", La Singularidad Activa Total. (Rendimiento Físico Crudo)
Instaura subparticiones nativas reales `/` y de boot, en la arquitectura hardware del Pendrive/SSD externo exactamente a imitación de montarlo puramente encima cualquier portátil PC. Destina el Kernel al metal.
*   **Fortalezas Fundamentales:** Fluidifica en el tiempo los márgenes térmicos del procesado, eliminando compuertas teóricas por emulación comprimida. Habilita una configuración nativa robustísima sobre el instalador por defecto logrando encriptar por completo de hardware-to-metal el OS total desde de su origen primigenio usando (LUKS FDE Full Disk).
*   **Contraindicaciones y Perjuicios Críticos:** Recluta una obligatoriedad impírica de alta tecnología como adaptadores rápidos M.2 SDD-to-USB ya que destruirá cualquier memoria simple de supermercado estresándola hasta el derrumbamiento NAND en pocas decenas de horas de instalación pesada. Supone el riesgo principal documentado (ver apartados técnicos del instalador ubuntu) de arrastre por sobreescritura accidental o parasitaria del sub-Gestor central GRUB afectando y corrompiendo en el arranque al MBR maestro propio del anfitrión Windows / Linux si al hacerlo accidentalmente no ha habido desconexión del disco interno.

---

## 4. Metodología Ensamblaje Opción A: Base "Live-USB Persistent"

Si se abraza la portabilidad estándar sobre pendrives cotidianos y en seguridad: Desde Ubuntu 20.04 en adelante (vigente en el núcleo 24.x y 25.x), el sistema se auto-regirá con tal que exista una partición precreada estipulada rígidamente formateada en kernel como "Ext4" y una Label unificada que llame por nombre inexcusablemente literal de: `writable`.

### Metodo A.1: "Pila de Software mkusb" en SO base Debian.
(Apropiada y Robusta)

Dado que mkusb milita en PPA's de Ubuntu, en la emulación a instalar sobre Debian general, la compilación necesita acoplar llaves públicas externas.

```bash
# 1. Empalmar infraestructura de las llaves GPG públicas oficiales dirmngr
sudo apt install dirmngr  
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 54B8C8AC

# 2. Inyectar list genérico al núcleo apt del repo mkusb (Rama Focal testada)
echo "deb http://ppa.launchpad.net/mkusb/ppa/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/mkusb.list

# 3. Empalmar actualización de cabeceras e integrar el tool
sudo apt update  
sudo apt install mkusb usb-pack-efi
```

Desbloquear por sudo `mkusb` como App del instalador. Navegar la jerarquía de ventanas hacia (`Install`) -> (`Persistent Live (Ubuntu/Debian)`). Señala la flag ISO de tu archivo local y dirige su mirilla bajo la estructura de discos de un USB diáfano de host y expande bajo limitante del 100% libre, el particionado de datos persistente.

### Metodo A.2: Foso Terminal Exclusivo (Expertos Puros CLI)

Si se elude manchar el "deb" general del host agregando PPA's extraños, la compilación forja el pendrive manualmente invocando la utilidad nativa de escritura base `dd` concatenada junto con editores de la tabla principal `fdisk` (ej: dev = `sdX` extraíble):

```bash
# Paso Uno. Intervención pura volcada con escritura ISO block destruyendo la unida base.
sudo dd if=xubuntu-25.10-minimal-amd64.iso of=/dev/sdX bs=4M status=progress

# Paso Dos. Estirar fronteras base abriendo fdisk sobre la unida y fijando hueco "writable".
sudo fdisk /dev/sdX
  # Input interactivo fdisk de secuencias de comandos crudas:
  # Pulsar [n] (new) -> [p] (partición prim.) -> [3] (Tercer bloque logico por norma de dd ubuntu)
  # Pulsar [Enter] ciego a sector principio -> y un [Enter] extendido al fin block max.
  # Pulsar [w] salvando directiva binaria y saliendo del daemon de terminal.

# Paso Tres. Asignación del archivo formato sobre el target modificado a Extensión 4.
sudo mkfs.ext4 -L writable /dev/sdX3
```

**[IMPORTANTISIMO CORRECCION AL ARRANQUE MANUAL METHOD A.2]**
El bootloader de arranque GRUB incrustado desde la factoría ISO estándar del sistema no acopla una inteligencia automatizada por bandera para inspeccionar externamente espacios grandes en la variante 3 precrecada sin PPA's. Si un preparador deja escalar y el SO corre bajo este setup y descarga 5GB de datos web, rellenará fatalmente los confines de la memoria RAM emulada temporal (Particion "/"), agotando recursos al instante e ignorando tu macro-espacio nuevo de 32GB `writable` (que es ajeno al archivo comprimido root en su ceguera configuracional).

**La Solución de inyección semántica paramétrica temporal:** 
En los segundos del menú host negro ("Try Or Install Xubuntu") se anula apretar [Enter] de frente. Posicionado en Try Ubuntu presionar por teclado la tecla editora paramétrica `[e]`. En esa terminal interna rastrea con cursores las letras hasta identificar la cabecera del driver operativo por excelencia y ancla la variable a fuego. (La línea típicamente comienza por "`linux`" finita en la amalgama de parámetros pasivos "`quiet splash ---`").
Modificando el entorno adjuntando literamente "`persistent`" sin aspas de forma que se contenga en las sublistas paramétrica del kernel:
Ejemplo resultando en : `...... quiet splash persistent ---`
Pulsamos F10 o `Ctrl+x` desencadenando ruteo EFI operativo por fin a toda su potencia hacia el Ext4 base de apoyo.
*(El script maestro inyectante futuro `install.sh` dominará permanentemente un parche temporal hacia el grub.cfg subsituyendo esta pesadez efímera)*.


---

## 5. Metodología Ensamblaje Opción B: "Full System Install" (Nativo Extractor Host)

Sujeto primiramente a entornos de Unidades Flash ultrarápidas o Unidades SSD vía USB type-C M2.

1.  **Paso Efímero Transitorio:** Forjado de material flasheable instalador convencional (`Balena Etcher` `Rufus` etc.) de un Pendrive Auxilar A pasivo con la ISO mínima.  
2.  **Extracción Física de Hardware (Inquebrantable):** Se extingue térmicamente la torre PC y mediante remoción de chasis, se extirpa, afloja, o desvinculan manualmente y por cable físico las acometidas (SATA / Power / NVMe) de CADA disco duro principal de trabajo y OS de la estructura primaria general de la habitacíón de la casa. Si no se actúa esta interrupción, como se avisó anteriormente ante una injerencia del cargador GRUB nativo que entrelace la instalación EFI maestra, rebotará los gestores de arraque perimiendo las instancias funcionales operativas de Windows o Debian en todo el anfitrión y descontrolando el registro boot local asimilando el disco esclavo como central y secuestrandolo a su merced.
3.  **Encadenamiento Visual y Cifrado de Flujo Absoluto:**
    *   Sondear pendrive pasivo A encendiendo hacia el menú genérico *Try Or Install*  y encadenando tras los subsistemas un anclaje por parte del Pendrive Definitivo SSD (El B). 
    *   En las casillas topológicas selectivas, bajo asunción del botón "Más características Opciones Especiales / Borrar Todo el Disco e Instalar Base" enfilar de reojo bajo el flag al target selectivo apuntando de plano el identificador extacto del pendrive "B" Destino definitivo.  
    *   (Si queremos cifrados holísticos para omitir Bóvedas modulares como explicamos antes, inyectaremos parámetros al click ("Borrados/Seleccionar LVM con clave FDE Encrypt Disk Password LUKS) incautando e inhibiendo genéricamente la unidad global hasta contraseñas blindadas maestras".
4.  Expansión al finalizar al 100%, apagar forzadamente. Recalibrar cables y resucitar de host a los ordenadores nativos atornillando o anidando a bahías el SSD original. La estación SSD auxiliar prepper de alta valía ya estará configurado.

A partir de poseer un Operador validado por una de ambas vías con espacio (Se comprueba en Xubuntu con `df -h /` atestiguando la enorme carga libre). Se procede bajo la terminal libre recién encendida un parche inicial hacia las carpetas base del proyecto antes de automatizar con scripts:

```bash
sudo apt update  
sudo apt install cryptsetup curl wget aria2 jq flatpak rsync libreoffice vlc evince -y  
sudo apt install $(check-language-support -l es) -y  
mkdir -p ~/refugiOS/{Apps,Conocimiento,Mapas,IA,Bovedas,Scripts}
```

---

## 6. Testing y Validación Rápida Vía Simuladores de VM (QEMU BIOS)

Como medida altamente proactiva del dev para eludir encender / apagar en pruebas eternas, un método resolutivo que afianza al preparador su ensamblaje directo y los script reside en ejecutar la prueba del USB al instanciarla bajo una ventana de Virtual Machine a nivel Host sin desmontarlo.

**Advertencia Máster Pre-Simulación por QEMU en Entornos Linux Boot OS y UEFI Files:**
Al invocar mediante un paquete crudo virtual base sin modificar al DAEMON qemu base, este trata por sustrato base y limitante arquitectónica levantar o asimilar que la unidad anidada rutea por bios lógicas "SeaBios / Legacy Bios antiguas". Sabiendo que refugiOS es altamente dependiente y pre compila matrices efímeras modernas en modo unificado "EFI/UEFI" si arrancamos genéricamente estallarán excepciones por inconsistencia geométrica y `unknown filesystem rescue> `.  Para arreglar esta falla de VM instalamos en la máquina host central el firmware oficial de UEFI y orquestamos el parche OVMF.

**Paso Uno: Topografía USB Genérica. Identificación Extensa:**
Rastrear sin montar al USB. El comando maestro es unificado `lsblk`, detectando si bajo listados su dispositivo es el `sdb`, `sdc` y se desvincula.

**Paso Dos: Corrientes de Afloramiento bajo Instalaciones QEMU:**

Seleccionamos la arquitectura general desde donde operaremos esta simulación local y lanzamientos:

*(Basado en Sistemas Debian u Ubuntu Host)*
```bash
sudo apt update && sudo apt install qemu-system-x86 qemu-kvm ovmf  
# Lanza en UEFI / asigna 4 RAM y dirige sobre un vector Raw.
sudo qemu-system-x86_64 -enable-kvm -m 4096 -bios /usr/share/ovmf/OVMF.fd -drive file=/dev/sdc,format=raw
```

*(Basado en Arquitecturas Fedorales o Red Hat Server C-OS)*
```bash
sudo dnf install qemu-kvm edk2-ovmf  
sudo qemu-kvm -m 4096 -bios /usr/share/edk2/ovmf/OVMF_CODE.fd -drive file=/dev/sdc,format=raw
```

*(Basado sobre Pacman en Endeavour u ArchLinux host)*
```bash
sudo pacman -S qemu-desktop edk2-ovmf  
sudo qemu-system-x86_64 -enable-kvm -m 4096 -bios /usr/share/edk2-ovmf/x64/OVMF_CODE.fd -drive file=/dev/sdc,format=raw
```

**Diagnósticos Resolutivos Frecuentes:**
*   *"No Pude Accesible Virtual KVM Mode module hardware Exception":* Corresponde a una limitante empírica severa pasiva implantada desde fábrica y desactivada por software de placa base host. El Virtualizer Hardware o VT-x en arquitecturas genéricas Intel o Sub-Modos anidables `SVM` Mode en las CPU matrices AMD de RYZEN etc.. En reiniciar desde BIOS y levantar switches "Enabled" del micro resolvemos el acceso pasivo con efectividad.
*   *"Inhibición e Hecatombe Computacional (El peligro letal sda):"* Como se describió genialmente, es un atentado total usar ciegamente `sdX` en los comandos sin saber por `lsblk` si el disco que mandamos al daemon a reescribir por encima es literalmente la carpeta raíz `sda` / local Host activo principal, destrozando toda la computadora al ser una sobreexcitación.
*    *"Warnings por formatos abstractos incompatibles":* Usar pasivas clásicas como invocaciones genéricas `-hda`/`-hdb` como emulador rígido no operan sobre dispositivos de hardware nativo enchufado. Emplearemos siempre para bloques externos matrices literales por el acople estricto: `-drive file=/dev/sdX,format=raw`.
