# Open Knowledge Format (OKF)

### 📖 [Leer la especificación de Open Knowledge Format v0.1 → SPEC.md](SPEC.md)

> **Este repositorio trata principalmente sobre el [Open Knowledge Format
> (OKF)](SPEC.md).**
>
> OKF es un **formato universal e independiente de proveedor** para
> representar conocimiento como archivos markdown planos con frontmatter
> YAML. **No está vinculado a ningún agente, framework, proveedor de
> modelos ni sistema de servicio en particular**. El objetivo es simple:
>
> - **Cualquiera puede producir** OKF — personas escribiendo a mano,
>   agentes construidos sobre cualquier framework (Google ADK, LangChain,
>   personalizado), pipelines de exportación desde catálogos existentes
>   (Dataplex, Unity Catalog, Collibra, …), o scripts que recorren una
>   base de datos.
> - **Cualquiera puede servir y consumir** OKF — un servidor de archivos
>   estáticos, una interfaz de gestión de conocimiento (Obsidian, Notion,
>   MkDocs), un LLM cargando archivos en contexto, un índice de búsqueda,
>   o un visor de grafos como el incluido en este repositorio.
>
> El agente que se describe a continuación es una **prueba de concepto**
> que demuestra *una* forma de producir bundles OKF automáticamente. El
> formato en sí es la contribución; este agente y el visualizador existen
> para hacer el formato tangible en ambos extremos — producción y consumo.
>
> **Ver OKF en práctica** — tres bundles listos para explorar producidos
> por este agente, incluidos en [`bundles/`](bundles/):
>
> - [`bundles/ga4/`](bundles/ga4/) — dataset de comercio electrónico GA4
>   ([viz.html](bundles/ga4/viz.html))
> - [`bundles/stackoverflow/`](bundles/stackoverflow/) — dataset público
>   de Stack Overflow ([viz.html](bundles/stackoverflow/viz.html))
> - [`bundles/crypto_bitcoin/`](bundles/crypto_bitcoin/) — bloques y
>   transacciones de Bitcoin
>   ([viz.html](bundles/crypto_bitcoin/viz.html))

## ¿Por qué OKF?

OKF representa el conocimiento de catálogo como archivos markdown planos
con frontmatter YAML, organizados en una jerarquía de directorios. Esta
elección desbloquea varias propiedades difíciles de obtener con un
almacén de metadatos gestionado por un servicio:

- **Legible por humanos y agentes.** Ningún SDK ni lenguaje de consulta se
  interpone entre el lector y el contenido. Un ingeniero puede hacer `cat`
  de un concepto; un LLM puede ingerirlo textualmente en su contexto.
- **Controlable por versiones de forma nativa.** Los bundles viven en git.
  Pull requests, diffs línea por línea, blame y flujos de revisión
  simplemente funcionan — la curación del conocimiento se convierte en una
  actividad normal de ingeniería de software.
- **Portable y libre de dependencia de proveedor.** Un bundle es un
  directorio. Envíalo como tarball, alójalo en cualquier repositorio,
  móntalo desde cualquier sistema de archivos o sincronízalo con cualquier
  sistema que maneje archivos. Ninguna API propietaria se interpone entre
  tú y tus metadatos.
- **Mezcla datos estructurados y no estructurados deliberadamente.** Usa
  frontmatter para los pocos campos que quieras consultar, filtrar o
  indexar (`type`, `resource`, `tags`, `timestamp`); usa el cuerpo
  markdown para la prosa, esquemas y consultas de ejemplo que los LLMs y
  humanos realmente leen.
- **Mínimamente opinado, libremente extensible.** Un conjunto reducido de
  claves requeridas asegura la interoperabilidad, pero los bundles pueden
  llevar claves de frontmatter adicionales arbitrarias y secciones de
  cuerpo arbitrarias sin romper a los consumidores.
- **Se compone con herramientas existentes.** Muchas herramientas de
  conocimiento — Notion, Obsidian, MkDocs, Hugo, Jekyll — ya manejan
  markdown con frontmatter YAML, por lo que los bundles pueden ser
  explorados, editados o renderizados sin una interfaz personalizada.
- **Revelación progresiva incorporada.** Los archivos `index.md`
  generados automáticamente permiten que un agente o humano navegue la
  jerarquía un nivel a la vez en lugar de cargar el bundle completo en
  contexto.
- **Forma de grafo, no solo de árbol.** Los conceptos se enlazan entre sí
  mediante enlaces markdown normales, expresando relaciones más ricas que
  la relación padre/hijo implícita en la estructura de directorios.

El efecto neto es que los agentes de referencia, los agentes de consumo y
los humanos colaboran sobre los mismos artefactos de la misma manera en
que ya colaboran sobre código fuente.

## Instalación

```
python3.13 -m venv .venv
.venv/bin/pip install --index-url https://pypi.org/simple/ -e .[dev]
```

## Credenciales

- BigQuery: `gcloud auth application-default login` más un proyecto para
  facturación (`gcloud config set project <id>`). Los datasets públicos son
  legibles, pero el proyecto del llamante es facturado por los bytes
  consultados.
- Gemini: establece `GEMINI_API_KEY` (AI Studio) **o** usa Vertex AI
  configurando `GOOGLE_GENAI_USE_VERTEXAI=true`,
  `GOOGLE_CLOUD_PROJECT=<id>` y `GOOGLE_CLOUD_LOCATION=<region>`.

## Cómo funciona el agente de referencia

El agente de referencia se ejecuta en dos pasadas. La **pasada BQ**
escribe un documento OKF por concepto que la fuente anuncia, usando
únicamente metadatos de BigQuery. La **pasada web** luego ejecuta el LLM
como su propio rastreador: recibe una lista de URLs semilla (provistas
mediante `--web-seed` o `--web-seed-file`), recupera las semillas
mediante la herramienta `fetch_url`, y decide qué enlaces salientes vale
la pena seguir según si parecen documentación autorizada para los
conceptos existentes. Por cada página que recupera, el agente elige (a)
enriquecer uno o más documentos de conceptos existentes, (b) crear un
documento independiente `references/<slug>`, o (c) omitir. Un límite
estricto `--web-max-pages` y un filtro de hosts permitidos del mismo
dominio (configurable mediante `--web-allowed-host`) se aplican dentro de
la herramienta, por lo que el agente no puede excederse. Usa `--no-web`
para omitir la pasada web.

## Ejecución

Invocación mínima — apunta a un dataset de BigQuery y un directorio de
salida para el bundle. Las semillas para la pasada web son explícitas;
omítelas (o pasa `--no-web`) para ejecutar solo BQ:

```
.venv/bin/python -m reference_agent enrich \
    --source bq \
    --dataset <project>.<dataset> \
    --web-seed-file <path/to/seeds.txt> \
    --out ./bundles/<name>
```

Itera sobre un solo concepto agregando `--concept <type>/<name>` (por
ejemplo, `--concept tables/events_`); se puede repetir.

## Muestras

Cada muestra combina una **receta** (`samples/<name>/`, con las URLs
semilla y el comando `enrich` exacto) con el **bundle producido**
(`bundles/<name>/`) que la receta generó. Abre la receta para reproducir;
abre el bundle para explorar el resultado directamente.

- **GA4 Google Merchandise Store** — dataset público de comercio
  electrónico, sembrado con URLs canónicas de documentación de
  GA4 BigQuery Export.
  · [receta](samples/ga4_merch_store/README.md)
  · [bundle](bundles/ga4/)
  · [viz.html](bundles/ga4/viz.html)
- **Stack Overflow** — dataset público (espejo del Stack Exchange Data
  Dump), sembrado con las referencias canónicas de esquema de la
  comunidad. Ejercita el enriquecimiento de múltiples conceptos desde
  páginas de documentación transversales.
  · [receta](samples/stackoverflow/README.md)
  · [bundle](bundles/stackoverflow/)
  · [viz.html](bundles/stackoverflow/viz.html)
- **Bitcoin (crypto)** — dataset público (bloques, transacciones,
  entradas, salidas) del pipeline `bitcoin-etl`. Ejercita relaciones de
  clave foránea entre tablas en prosa.
  · [receta](samples/crypto_bitcoin/README.md)
  · [bundle](bundles/crypto_bitcoin/)
  · [viz.html](bundles/crypto_bitcoin/viz.html)

## Visualización

El subcomando `visualize` renderiza cualquier bundle OKF como un
**archivo HTML interactivo autocontenido** — un solo archivo, sin
backend, sin instalación del lado del visualizador. Ábrelo en cualquier
navegador moderno, compártelo como artefacto, alójalo en un servidor de
archivos estáticos, o haz commit junto al bundle (como hace este
repositorio).

El visor es en sí mismo un *consumidor* de prueba de concepto de OKF,
reflejando la forma en que el agente de referencia es un *productor* de
prueba de concepto. Los bundles OKF pueden ser consumidos por cualquier
cosa que lea markdown; esta es solo una forma posible.

### Qué muestra

- Un **grafo dirigido por fuerzas** de cada concepto en el bundle, con
  nodos coloreados por tipo (datasets, tables, references, …) y aristas
  dirigidas dibujadas a partir de cada enlace cruzado en los cuerpos
  markdown.
- Un **panel de detalle** para el concepto seleccionado mostrando su
  frontmatter (descripción, enlace al recurso, etiquetas) y su cuerpo
  markdown renderizado — con enlaces internos
  `[…](/path/to/concept.md)` reconectados para navegar dentro del visor
  en lugar de seguir la ruta.
- Una lista de **backlinks "Citado por"** bajo cada concepto (calculada a
  partir del reverso del grafo de enlaces).
- Un **cuadro de búsqueda** (busca por título, id de concepto y
  etiquetas), un **filtro por tipo**, y layouts de grafo intercambiables
  (cose / concentric / breadth-first / circle / grid).

### Generar

```
.venv/bin/python -m reference_agent visualize --bundle ./bundles/<name>
```

Esto escribe `bundles/<name>/viz.html`. Opciones:

| Opción         | Valor por defecto      | Descripción                                         |
|----------------|------------------------|-----------------------------------------------------|
| `--bundle`     | *(requerido)*          | Directorio raíz del bundle.                         |
| `--out`        | `<bundle>/viz.html`    | Ruta del archivo HTML de salida.                    |
| `--name`       | nombre del directorio del bundle | Nombre mostrado en el encabezado del visor. |

Ejemplo, escribiendo la salida en otro lugar y sobreescribiendo el
encabezado:

```
.venv/bin/python -m reference_agent visualize \
    --bundle ./bundles/crypto_bitcoin \
    --out /tmp/btc.html \
    --name "Bitcoin OKF"
```

### Cómo está construido

El HTML incrusta el bundle como un blob JSON y usa
[Cytoscape.js](https://js.cytoscape.org/) para el grafo y
[marked](https://marked.js.org/) para el renderizado de markdown en el
navegador, ambos cargados desde un CDN. Ningún dato sale de la página; el
bundle se parsea una vez en el momento de la generación y se serializa en
el archivo.

## Tests

```
.venv/bin/pytest
```
