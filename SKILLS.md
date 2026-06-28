# OKF Simple: Referencia del Código Fuente y Guía de Habilidades para Agentes

Bienvenido a la implementación de referencia simplificada de **Open Knowledge Format (OKF)**. Este repositorio contiene las herramientas, ejecutores e interfaces de línea de comandos necesarios para construir, enriquecer y visualizar catálogos de metadatos autocontenidos (paquetes de conocimiento) para conjuntos de datos.

OKF representa metadatos e información curada como un directorio de archivos Markdown que contienen frontmatter YAML. Esta guía explica cómo interactuar con el sistema a través de su API de Python, utilizar sus subcomandos de interfaz de línea de comandos (CLI) y aprovechar el pipeline de generación de catálogos dentro de flujos de trabajo automatizados con agentes (vibe coding).

---

## 1. Visión General de la Estructura de Directorios

El código fuente está organizado de la siguiente manera:
* `src/reference_agent/` - Directorio principal del código fuente que contiene:
  * `cli.py` - Definiciones de la interfaz de línea de comandos y puntos de entrada.
  * `runner.py` - Orquesta los pases de enriquecimiento (basado en fuente + basado en web) y la regeneración de índices.
  * `agent.py` - Configura los agentes de ADK (Agent Development Kit).
  * `bundle/` - Maneja el análisis de documentos (`document.py`), rutas de archivos (`paths.py`), generación de índices (`index.py`) y descripciones con IA (`synthesizer.py`).
  * `sources/` - Adaptadores para activos de datos subyacentes (por ejemplo, fuente de BigQuery en `bigquery.py`).
  * `tools/` - Gestión de contexto y funciones invocables por agentes.
  * `viewer/` - Generador de visualizaciones (`generator.py`) y recursos de interfaz de usuario.

---

## 2. Referencia de la API Directa de Python

Puedes conducir programáticamente la creación de catálogos, extracción de metadatos, rastreo web y regeneración de índices usando la API de Python.

### 2.1 Importación de Módulos y Configuración de Contexto

Para ejecutar cualquier función a nivel de herramienta, primero debes inicializar un contexto a nivel de espacio de trabajo que contenga el proveedor de fuente activo y el directorio de salida del bundle.

```python
from pathlib import Path
from reference_agent.sources.bigquery import BigQuerySource
from reference_agent.tools.context import set_context

# 1. Initialize a data source (e.g., BigQuery)
# 'dataset' must be in 'project.dataset' format.
# 'billing_project' is optional (defaults to the Application Default Credentials project).
source = BigQuerySource(
    dataset="bigquery-public-data.crypto_bitcoin",
    billing_project="my-gcp-project"
)

# 2. Define the output bundle directory
bundle_root = Path("./my_bitcoin_bundle")

# 3. Set the global tool context (this maps the source and bundle root)
set_context(source, bundle_root)
```

### 2.2 Funciones a Nivel de Herramienta (`reference_agent.tools`)

Una vez configurado el contexto, puedes importar e invocar las siguientes funciones. Estas son idénticas a las herramientas proporcionadas a los agentes de ADK:

#### `list_concepts() -> list[dict[str, Any]]`
Lista todos los conceptos publicados por la fuente activa (por ejemplo, el dataset en sí y sus tablas).
* **Retorna:** Una lista de diccionarios de referencia de conceptos:
  ```python
  [
      {
          "id": "datasets/crypto_bitcoin",
          "type": "BigQuery Dataset",
          "resource": "https://bigquery.googleapis.com/v2/projects/bigquery-public-data/datasets/crypto_bitcoin",
          "hint": {"dataset_project": "bigquery-public-data", "dataset_id": "crypto_bitcoin"}
      },
      {
          "id": "tables/blocks",
          "type": "BigQuery Table",
          "resource": "https://bigquery.googleapis.com/v2/projects/bigquery-public-data/datasets/crypto_bitcoin/tables/blocks",
          "hint": {"wildcard": False, "table_id": "blocks"}
      }
  ]
  ```

#### `read_concept_raw(concept_id: str) -> dict[str, Any]`
Obtiene el esquema estructurado sin procesar y los metadatos directamente desde la fuente.
* **Parámetros:** `concept_id` (la ruta separada por barras, por ejemplo, `'tables/blocks'`).
* **Retorna:** Un diccionario que contiene detalles como campos del esquema, conteo de filas, tiempo de creación, campos de partición, etc.

#### `sample_rows(concept_id: str, n: int = 5) -> dict[str, Any]`
Recupera una pequeña muestra de filas del activo subyacente.
* **Retorna:** `{"rows": [...], "note": ""}` donde rows es una lista de diccionarios de filas convertidos a cadena de texto.

#### `read_existing_doc(concept_id: str) -> dict[str, Any] | None`
Lee un documento OKF en formato markdown existente del directorio de salida del bundle si existe.
* **Retorna:** `{"frontmatter": dict, "body": str}` o `None` si no existe un documento previo.

#### `write_concept_doc(concept_id: str, frontmatter: dict[str, Any], body: str) -> dict[str, Any]`
Escribe o aumenta un documento OKF en formato markdown.
* **Validación:** Valida que las claves requeridas del frontmatter (`type`, `title`, `description`, `timestamp`) existan.
* **Protección de Aumentación:** Si se invoca durante un pase web sobre un documento existente de BigQuery Table, previene sobreescrituras que eliminen campos del esquema o enlaces de citación.
* **Retorna:** `{"path": str, "bytes": int}` o `{"error": str, "concept_id": str}` si la validación falla.

#### `fetch_url(url: str) -> dict[str, Any]`
Obtiene el contenido de una página web como markdown y lista todos los enlaces salientes.
* **Restricciones:** Respeta automáticamente el presupuesto de rastreo de la sesión (`max_pages`), los hosts permitidos, los prefijos de ruta permitidos y la profundidad de distancia de saltos.
* **Retorna:** Detalles exitosos de la página o un diccionario de rechazo que contiene `{"error": "<razón>"}`.

### 2.3 Regeneración Programática de Índices

```python
from reference_agent.bundle.index import regenerate_indexes

# Regenerate all index.md files in the bundle directory.
# Uses Gemini to auto-synthesize summaries for folders containing multiple child concepts.
written_paths = regenerate_indexes(
    bundle_root=Path("./my_bitcoin_bundle"),
    model="gemini-flash-latest"
)
```

### 2.4 Generación Programática de Visualizaciones

```python
from reference_agent.viewer import generate_visualization

# Walks the bundle and compiles a self-contained HTML network graph
stats = generate_visualization(
    bundle_root=Path("./my_bitcoin_bundle"),
    out_path=Path("./my_bitcoin_bundle/viz.html"),
    bundle_name="Crypto Bitcoin Bundle"
)
print(f"Wrote {stats['concepts']} concepts, {stats['edges']} edges → {stats['bytes']} bytes")
```

### 2.5 Ejecutor Programático del Pipeline

También puedes usar la clase `ReferenceRunner` para orquestar el flujo completo (enriquecer conceptos seleccionados, ejecutar el pase de rastreo web y construir archivos de índice).

```python
from reference_agent.runner import ReferenceRunner
from reference_agent.sources.bigquery import BigQuerySource

runner = ReferenceRunner(
    source=BigQuerySource(dataset="bigquery-public-data.crypto_bitcoin"),
    bundle_root=Path("./my_bitcoin_bundle"),
    model="gemini-flash-latest",
    web_seeds=["https://en.bitcoin.it/wiki/Main_Page"],
    web_max_pages=15,
    verbose=True
)

# Run the complete enrichment flow for all discovered concepts
runner.enrich_all()
```

---

## 3. Subcomandos del CLI

El CLI está registrado bajo el ejecutable `reference-agent`. Ofrece dos subcomandos principales: `enrich` y `visualize`.

### 3.1 `enrich`

Obtiene metadatos de una fuente, invoca agentes LLM para escribir documentación de conceptos, ejecuta el rastreo/ingesta web y regenera los índices de directorio.

```bash
reference-agent enrich \
  --source bq \
  --dataset <project>.<dataset> \
  --out <output-directory-path> \
  [options]
```

#### Opciones Principales:
* `--source`: Actualmente soporta `bq` (BigQuery).
* `--dataset`: La referencia del dataset (`project.dataset`).
* `--billing-project`: Proyecto opcional de Google Cloud para facturar consultas (por defecto usa las credenciales ADC).
* `--out`: Directorio raíz para la salida del bundle OKF compilado.
* `--concept`: Opcional. Ejecuta el enriquecimiento *solo* para este ID de concepto (por ejemplo, `--concept tables/blocks`). Se puede especificar múltiples veces.
* `--model`: El ID del modelo Gemini a usar (por defecto: `gemini-flash-latest`).
* `-v`, `--verbose`: Habilita logs detallados que muestran eventos de prompt, llamadas a herramientas y partes de texto del LLM.

#### Opciones del Rastreador Web e Ingesta:
* `--no-web`: Omite el pase de rastreo/ingesta web por completo.
* `--web-seed`: Una URL semilla desde la cual iniciar el rastreo. Se puede especificar múltiples veces.
* `--web-seed-file`: Ruta a un archivo de texto que contiene URLs semilla (una por línea, se permiten comentarios con `#`).
* `--web-max-pages`: Número máximo de páginas a obtener (por defecto: `100`).
* `--web-allowed-host`: Nombres de host adicionales que el rastreador puede visitar. Por defecto, solo rastrea los hosts netloc de las semillas.
* `--web-allowed-path-prefix`: Filtro de prefijo de ruta (por ejemplo, `/docs/`). Si se especifica, solo se obtienen URLs que comienzan con este prefijo.
* `--web-denied-path-substring`: Subcadenas a bloquear (por ejemplo, `/login`, `/pricing`).
* `--web-max-depth`: Distancia máxima de saltos desde las URLs semilla (por defecto: `2`). Las semillas tienen profundidad `0`.

### 3.2 `visualize`

Analiza un bundle OKF existente y genera un grafo de red interactivo autocontenido en un único archivo HTML.

```bash
reference-agent visualize \
  --bundle <bundle-root-directory> \
  [--out <output-html-path>] \
  [--name <display-name>]
```

* `--bundle`: Ruta al directorio raíz del bundle OKF generado.
* `--out`: Ruta de destino para el archivo HTML. Por defecto: `<bundle-root-directory>/viz.html`.
* `--name`: Título personalizado opcional que se muestra en el encabezado de la visualización.

---

## 4. Flujo de Trabajo de Vibe Coding: Documentando un Dataset en OKF

Si eres un agente de programación externo o estás escribiendo un script para documentar un dataset desde cero en formato OKF, sigue este flujo de trabajo estructurado paso a paso:

### Paso 1: Descubrir los Conceptos de la Fuente
Inicializa tu fuente e inspecciona qué conceptos están presentes. Llama a `list_concepts()` para recuperar el catálogo.
* *Objetivo:* Identificar el concepto del dataset (`datasets/<dataset_id>`) y los conceptos de tabla (`tables/<table_id>`).

### Paso 2: Extraer Esquema y Datos de Muestra
Para cada concepto de tabla:
1. Llama a `read_concept_raw(concept_id)` para extraer detalles técnicos: campos, columnas anidadas, claves de partición, conteo de filas y tamaños de datos.
2. Llama a `sample_rows(concept_id, n=3)` para obtener valores concretos. Esto ayuda a clarificar el contenido de campos de texto ambiguos, banderas de enumeración o rangos de marcas de tiempo.

### Paso 3: Verificar Documentación Existente
Llama a `read_existing_doc(concept_id)`.
* *Regla:* Nunca sobreescribas documentos existentes a ciegas. Trátalos como línea base. Refina, agrega o corrige su contenido.

### Paso 4: Escribir los Documentos OKF Principales
Compila el archivo markdown para cada concepto y llama a `write_concept_doc(concept_id, frontmatter, body)`.

#### Frontmatter Requerido:
* `type`: por ejemplo, `BigQuery Table` o `BigQuery Dataset`.
* `title`: Un título limpio y legible para humanos.
* `description`: **Exactamente una oración** que resuma el concepto (se usa en los archivos de índice de carpeta).
* `timestamp`: Sin establecer (la herramienta lo completa automáticamente con la hora actual en formato UTC ISO 8601).

#### Secciones Requeridas del Cuerpo (en orden):
1. **Descripción en Prosa:** 1-3 párrafos que describan qué es el activo y su granularidad (por ejemplo, "Una fila por transacción").
2. **Sección `# Schema`:** Lista o tabla Markdown plana y legible de los campos. Para tipos RECORD, indenta o detalla los atributos anidados.
3. **Sección `# Common query patterns`:** 1-3 bloques de código SQL delimitados (` ```sql `) que muestren operaciones de consulta realistas.
4. **Sección `# Citations`:** Lista de fuentes. La primera citación debe ser el enlace `resource` del concepto.

### Paso 5: Ejecutar Rastreo e Ingestar Contexto Web
Si se proporcionan URLs semilla, ejecuta el flujo de ingesta web usando `fetch_url(url)` para navegar documentación y wikis de referencia:
1. Analiza el markdown obtenido para localizar referencias estructurales.
2. **Extraer Métricas:** Identifica métricas agregadas (por ejemplo, *Usuarios Activos Diarios*). Crea un documento de referencia en `references/metrics/<metric_slug>.md` que contenga el nombre, la descripción y la fórmula SQL concreta. Enlaza esta métrica desde la sección `# Metrics` de la tabla contribuyente.
3. **Extraer Rutas de Join:** Identifica relaciones. Crea un documento de referencia de join en `references/joins/<table_a>__<table_b>.md` (ordenamiento alfabético de nombres) que contenga la cláusula SQL `ON` concreta. Enlaza este join desde las secciones `# Joins` de ambas tablas.
4. **Crear Referencias Genéricas:** Crea un documento en `references/<ref_slug>.md` si un tema define algo referenciable por nombre (como códigos de enumeración) y es citado por múltiples tablas.
5. **Enlazar Conceptos Cruzados:** Teje enlaces entre páginas usando rutas de archivo *relativas al directorio* (por ejemplo, `[users](users.md)` o `[event parameters](../references/event_parameters.md)`). Nunca uses enlaces absolutos con `/`.

> [!IMPORTANT]
> **Reglas de Aumentación:** Al aumentar un concepto existente con información web, debes pasar el diccionario completo de frontmatter (preservando `type`, `title` y `resource` de forma literal) y preservar todos los encabezados `#` existentes del cuerpo. La herramienta bloqueará la escritura si eliminas campos del esquema o remueves citaciones.

### Paso 6: Regenerar Índices de Directorio
Invoca `regenerate_indexes(bundle_root)`. Esto crea un archivo `index.md` limpio en cada directorio que contiene enlaces a documentos hijos y subdirectorios, asegurando una divulgación progresiva.

### Paso 7: Construir la Visualización del Grafo de Red
Genera la interfaz interactiva usando `generate_visualization`. Abre el archivo `viz.html` resultante en un navegador web para revisar nodos, investigar relaciones, verificar la integridad de los enlaces cruzados y explorar detalles.
