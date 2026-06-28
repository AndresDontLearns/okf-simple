---
name: okf_simple
description: Manage and compile Open Knowledge Format (OKF) metadata catalog directories.
---

# Habilidad de Agente OKF Simple

Esta habilidad permite a los agentes descubrir, enriquecer, analizar y estructurar conjuntos de datos en **bundles de Open Knowledge Format (OKF)**. Los bundles OKF representan metadatos de catálogo y documentación como un árbol limpio de carpetas con archivos markdown que contienen frontmatter YAML.

---

## 1. Herramientas y Funciones Disponibles

Cuando esta habilidad está cargada, tienes acceso a las siguientes herramientas programáticas para manipular el contexto del bundle activo:

* **`list_concepts()`**: Lista todos los conceptos (datasets, tablas o referencias) disponibles en la fuente activa.
* **`read_concept_raw(concept_id)`**: Obtiene los metadatos estructurados del esquema sin procesar (columnas, tipos de datos, conteos) directamente del sistema subyacente (por ejemplo, BigQuery).
* **`sample_rows(concept_id, n=5)`**: Extrae algunas filas de datos de muestra para orientar las descripciones.
* **`read_existing_doc(concept_id)`**: Recupera cualquier documentación markdown OKF previamente escrita desde el disco local.
* **`write_concept_doc(concept_id, frontmatter, body)`**: Crea o actualiza un documento markdown OKF con frontmatter YAML estándar y secciones en markdown.
* **`fetch_url(url)`**: Recupera el contenido markdown de la página web y sus enlaces salientes, aplicando automáticamente límites de profundidad, presupuestos y restricciones de dominio.

---

## 2. Flujo de Trabajo Estándar de Enriquecimiento

Para construir un catálogo OKF de alta calidad, ejecuta siempre los pasos en la siguiente secuencia:

### Paso 1: Descubrir y Mapear
Identifica los conceptos presentes en el conjunto de datos llamando a `list_concepts()`. Anota sus IDs, tipos y enlaces a recursos.

### Paso 2: Leer Metadatos y Datos de Muestra
Para cada concepto objetivo:
1. Obtén los parámetros estructurados con `read_concept_raw(concept_id)`.
2. Extrae datos de muestra con `sample_rows(concept_id)`.
3. Verifica si existen documentos previos usando `read_existing_doc(concept_id)`.

### Paso 3: Escribir los Documentos Primarios de Conceptos
Escribe la documentación principal usando `write_concept_doc(concept_id, frontmatter, body)`.

* **Claves de Frontmatter Requeridas:** `type`, `title`, `description` (exactamente una oración), `timestamp`.
* **Secciones Markdown Requeridas:**
  1. Descripción en prosa (granularidad, rango temporal, contexto).
  2. `# Schema` (listas de columnas, registros anidados).
  3. `# Common query patterns` (de 1 a 3 bloques SQL realistas).
  4. `# Citations` (enlaces a especificaciones o endpoints sin procesar).

### Paso 4: Rastreo Web y Extracción de Conocimiento
Si se proporcionan semillas de rastreo, recupéralas usando `fetch_url(url)`. Sigue los enlaces salientes para recopilar detalles de referencia y extrae:
* **Métricas:** Crea un archivo de referencia de métrica en `references/metrics/<slug>.md` con frontmatter `tags: [metric]` y tipo `Reference`. El cuerpo debe contener la fórmula SQL concreta. Enlaza este archivo desde la sección `# Metrics` de las tablas correspondientes.
* **Joins:** Crea un archivo de referencia de join en `references/joins/<table_a>__<table_b>.md` (nombres ordenados alfabéticamente) con frontmatter `tags: [join]`. El cuerpo debe contener la cláusula `ON` exacta en SQL. Enlaza esto desde la sección `# Joins` de ambas tablas.
* **Referencias:** Crea `references/<ref_slug>.md` para enumeraciones generales, entidades de negocio o glosarios.

---

## 3. Reglas Estrictas de Operación

Como agente que ejecuta esta habilidad, **debes** cumplir con estas restricciones:

1. **Enlaces Cruzados Relativos:** Siempre enlaza conceptos hermanos o relacionados usando rutas relativas (por ejemplo, `[users](users.md)` o `[parameters](../references/event_parameters.md)`). Nunca uses rutas absolutas con `/`, ya que rompen los visualizadores de markdown sin conexión.
2. **Integridad de Enriquecimiento:** Al actualizar un documento existente con datos rastreados de la web:
   * Mantén todas las claves de frontmatter existentes textualmente (`type`, `title`, `resource`).
   * Preserva todos los encabezados `#` existentes.
   * No elimines columnas del esquema ni remuevas citas. La herramienta verifica esto y rechazará la escritura si se elimina algo.
3. **Sin Preámbulos ni Disculpas:** Al escribir archivos markdown, escribe texto limpio y directo. No incluyas razonamientos, disculpas ni comentarios en los archivos `.md`.
