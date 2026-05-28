# Elección del Medio de Instalación

Antes de instalar refugiOS necesitas elegir el **dispositivo físico** donde se ejecutará. Esta guía te ayudará a tomar la mejor decisión según tu presupuesto y necesidades.

> [!TIP]
> **Método más rápido:** La forma más sencilla de empezar es descargar la **[imagen pregenerada](https://refugios.ganso.org/refugios-base-16G-es.img)** y grabarla en un USB de al menos 16 GB. Consulta el **[README](../README.md)** para los pasos de inicio rápido.

> [!NOTE]
> Si vas a instalar refugiOS en una **Raspberry Pi**, el medio de instalación es distinto (tarjeta microSD o SSD vía HAT/USB). Consulta la **[Guía de Instalación en Raspberry Pi](Instalacion-Raspberry-ES.md#1-hardware-necesario)** para los detalles específicos de esa plataforma.

---

## 1. Tipo de Dispositivo: Pendrive vs SSD

La diferencia más importante no es la capacidad, sino el **tipo de memoria**:

*   **Recomendación de Oro:** Aunque un pendrive estándar funciona, lo ideal para un buen rendimiento es un **disco SSD de bolsillo** (o un adaptador USB para discos M.2 NVMe). Las memorias USB baratas se desgastan rápido bajo el uso constante de Linux y su velocidad de escritura es muy pobre.
*   **Pendrive (Memoria USB):** Es del tamaño de un pulgar, muy ligero y barato. Se calienta mucho y su velocidad cae drásticamente tras 5 minutos de uso.
*   **SSD de bolsillo:** Es algo más grande (como un mechero o una caja de cerillas), suele tener carcasa de metal y velocidades que no bajan de los 400 MB/s. Es una unidad de disco real, pero miniaturizada.

> [!WARNING]
> El método de **Instalación Nativa** (tanto en ISO Xubuntu como en imagen de sistema) no se recomienda en pendrives convencionales porque el "journaling" de Linux los destruirá en pocos meses. **Úsalo solo si tienes un SSD por USB.** El modo Live con persistencia es más seguro para pendrives estándar.

---

## 2. Capacidad y Contenido

El tamaño del dispositivo determina qué contenidos podrás almacenar:

| Capacidad | Contenido Posible | Perfil de Uso |
| :--- | :--- | :--- |
| **16 GB (Mínimo)** | Sistema base + WikiMed + Mapas básicos + IA ligera. Sin espacio para Wikipedia. | Unidad de emergencia básica |
| **32 GB (Equilibrado)** | Todo lo anterior + Wikipedia sin imágenes. Sin espacio para Wikipedia completa. | Respaldo funcional |
| **64 GB (Estándar)** | Wikipedia completa con imágenes + IA Phi-4-mini + WikiMed + Mapas. Espacio limitado para más contenido. | Uso diario recomendado |
| **128 GB o más** | Todo lo anterior + WikiHow + múltiples modelos de IA + mapas mundiales detallados. | Estación avanzada |

---

## 3. Consejos de Compra

### Qué buscar

*   **Versión de USB:** Busca siempre **USB 3.0, 3.1 o 3.2** (a veces marcados como "Gen 1" o "Gen 2"). El conector suele ser de color azul o rojo por dentro.
*   **Velocidad:** En la caja, busca velocidades de lectura superiores a **150 MB/s** y de escritura superiores a **50 MB/s**.
*   **Formato:** Los de carcasa metálica disipan mejor el calor durante un uso intensivo.

### Qué evitar

*   **USB 2.0:** Es desesperadamente lento para ejecutar un sistema operativo. Un arranque que tarda 30 segundos en USB 3.0 puede tardar 10 minutos en USB 2.0.
*   **Marcas desconocidas:** Huye de ofertas "demasiado buenas para ser verdad" de 1 TB por 10€; suelen ser estafas con capacidad real ínfima.

### Qué pedir en la tienda (o buscar en Amazon)

Si vas a una tienda física o buscas online, usa estas palabras mágicas para no fallar:

*   **En tienda física:** *"Quiero un disco SSD externo de bolsillo, que sea USB 3.2 y de al menos 64GB (o 128GB), con velocidad de lectura superior a 400 MB/s"*.
*   **En tiendas online:** Busca *"SSD Portátil 128GB USB 3.2"* o *"Unidad de estado sólido externa USB-C"*. Fíjate que en la descripción ponga **"SSD"** y no solo "Flash Drive" o "USB Stick".

### Estrategia de respaldo

Si tienes pendrives antiguos o más pequeños (16 GB), no los tires. Puedes dejarlos como **unidades de reserva** metidos en una mochila, en el botiquín o en el vehículo con el sistema básico. Lleva siempre contigo "el bueno" (SSD o USB 3.2 rápido) como unidad principal.

---

## 4. Opciones de Referencia y Presupuestos (España)

Para facilitar la elección, aquí tienes tres configuraciones recomendadas. Ten en cuenta que los precios en tecnología son muy volubles y sirven solo como orientación, y que en el momento de escribir esto (marzo/abril de 2026) los precios están sufriendo una tendencia al alza:

1.  **Opción Base (Económica / Réplicas):** 
    *   **Qué es:** Un pendrive USB 3.2 metálico de 32GB o 64GB (Ej: SanDisk Ultra Luxe o Kingston DataTraveler Kyson).
    *   **Para qué:** Ideal para tener **múltiples réplicas de seguridad baratas** del sistema base en mochilas, vehículos o botiquines. No recomendado para uso diario intensivo.
    *   **Precio Real 2026:** Entre **8€ y 20€**.
    *   *Nota:* Un modelo estándar de 64GB se localiza por unos **10€**. Las versiones de 32GB parten de los **14€**, subiendo hasta los **15€-25€** para los 64GB más rápidos. Modelos de plástico son más baratos (**8€**), pero su baja durabilidad no justifica el pequeño ahorro.

2.  **Opción Intermedia (Adaptador SATA):**
    *   **Qué es:** Un adaptador USB a SATA III (cable o carcasa) para conectar discos HDD o SDD de 2.5" o 3.5" existentes.
    *   **Para qué:** La mejor forma de **reciclar discos de ordenadores viejos** para tener un refugiOS de alta velocidad y gran capacidad para el día a día sin gastar mucho. Un SSD nos dará una velocidad de lectura y escritura comparable con un ordenador moderno, mientras que un HDD bien cuidado puede tener una durabilidad enorme (aunque tendremos que tener más cuidado con golpes o campos magnéticos).
    *   **Precio Real 2026:** Entre **10€ y 20€**, más el precio del disco duro que ya tengamos.
    *   *Nota:* Las carcasas básicas de aluminio se encuentran entre **5€ y 10€**. Los adaptadores de cable de alta fidelidad con soporte UASP oscilan entre los **15€ y 20€**.

3.  **Opción Premium (Unidad Principal):**
    *   **Qué es:** Un SSD Portátil dedicado de 250GB o un montaje DIY (NVMe + Carcasa).
    *   **Para qué:** Como **unidad principal de alto rendimiento**. Imprescindible para uso intensivo de modelos de IA complejos, Wikipedia completa con imágenes y mapas mundiales detallados.
    *   **Precio Real 2026:** Entre **60€ y 90€**.
    *   *Nota:* Los modelos premium "montados" suelen partir ya de los 500GB (**100€-150€**). La opción real de 250GB ronda los **65€**. Montar un módulo NVMe por piezas puede ascender a los **80€-90€**, siendo más caro pero permitiendo futuras actualizaciones.

### Comparativa de Rendimiento y Experiencia (2026)

| Perfil de Uso | Capacidad | Inversión (Est.) | Tiempo Instalación | Experiencia de Uso |
| :--- | :--- | :--- | :--- | :--- |
| **Distribución OS** | 32 GB - 64 GB | 10 € - 20 € | Una tarde completa | Con esperas continuas |
| **Reciclaje SSD** | 128 GB - 256 GB | 15 € (Solo adap.) | ~1 hora | Fluida (casi nativa) |
| **Alto Rendimiento** | 250 GB | 60 € - 90 € | < 45 minutos | Responsiva (como local) |

> [!IMPORTANT]
> Este ecosistema de precios refleja que el mercado de 2026 penaliza las capacidades más bajas. La diferencia de precio entre un pendrive lento y un SSD de 250GB es hoy una de las brechas de valor más importantes para el usuario final.

---

## 5. Implicaciones según el Método de Instalación

El tipo de dispositivo que elijas también influye en qué método de instalación te conviene más:

| Método de Instalación | Pendrive USB 3.x | SSD USB | Adaptador SATA |
| :--- | :--- | :--- | :--- |
| **Imagen pregenerada** (recomendado) | ✅ Recomendado | ✅ Recomendado | ✅ Recomendado |
| **ISO Live con Persistencia** | ✅ Recomendado para pendrives | ✅ Funcional | ✅ Funcional |
| **Imagen Nativa de Sistema** | ⚠️ Posible pero desgaste rápido | ✅ Recomendado para SSD | ✅ Recomendado para SSD |
| **Instalación Nativa XUbuntu** | ❌ No recomendado (journaling) | ✅ Solo con SSD | ✅ Solo con SSD |

> [!TIP]
> Para la mayoría de los usuarios, la **imagen pregenerada** es la mejor opción independientemente del dispositivo. Si tienes un **pendrive estándar**, la imagen pregenerada con autoexpansión funcionará bien. Si tienes un **SSD**, cualquier método ofrece buen rendimiento; la imagen pregenerada es la más rápida de empezar.

---

[Volver a la documentación](../README.md)
