# Open Knowledge Format (OKF)

**Versión 0.1 — Borrador**

OKF es un formato abierto, amigable tanto para humanos como para agentes, para representar
*conocimiento* — los metadatos, el contexto y la perspectiva curada que rodea
a los datos y sistemas. Está diseñado para ser escrito por personas, generado por
agentes, intercambiado entre organizaciones y consumido por ambos.

El formato es intencionalmente mínimal: un directorio de archivos markdown con
frontmatter YAML. No hay un registro de esquemas, ni una autoridad central, ni
herramientas obligatorias. Si puedes ejecutar `cat` sobre un archivo, puedes leer OKF; si
puedes hacer `git clone` de un repositorio, puedes distribuirlo.

---

## 1. Motivación

El espacio de representación del conocimiento para agentes de IA está evolucionando rápidamente,
y están surgiendo muchas convenciones incompatibles. OKF adopta la posición
de que el conocimiento se representa mejor en formatos comunes y accesibles,
establecidos, que sean:

- **Legibles** por humanos sin herramientas especiales.
- **Parseables** por agentes sin SDKs a medida.
- **Diferenciables** en control de versiones.
- **Portables** entre herramientas, organizaciones y a lo largo del tiempo.

El formato es mínimamente dogmático. Estandariza solo el conjunto reducido
de convenciones estructurales necesarias para hacer que un corpus de conocimiento
sea *autodescriptivo* — todo lo demás queda a criterio del productor.

### Objetivos

1. Definir un formato universal en el que los **agentes de enriquecimiento** puedan escribir.
2. Indicar cómo los **agentes de consumo** deben leerlo y recorrerlo.
3. Facilitar el **intercambio** de conocimiento entre sistemas y organizaciones.
4. Estandarizar el número reducido de campos **required** que deben estar
   presentes para que el contenido pueda ser consumido de manera significativa.

### No-objetivos

- Definir una taxonomía fija de tipos de conceptos.
- Prescribir infraestructura de almacenamiento, servicio o consulta.
- Reemplazar esquemas específicos de dominio (Avro, Protobuf, OpenAPI, etc.) —
  OKF los *referencia*; no los subsume.

---

## 2. Terminología

- **Knowledge Bundle** — Una colección jerárquica y autocontenida de
  documentos de conocimiento. Es la unidad de distribución.
- **Concept** — Una unidad individual de conocimiento dentro de un bundle. Se representa
  como un documento markdown. Puede describir un activo tangible (una tabla, una
  API), una idea abstracta (una métrica, un proceso de negocio) o cualquier cosa
  intermedia.
- **Concept ID** — La ruta del archivo del concepto dentro del bundle,
  sin el sufijo `.md`. Por ejemplo, `tables/users.md` tiene
  como concept ID `tables/users`.
- **Frontmatter** — Bloque de metadatos YAML delimitado por `---` al inicio de
  un archivo markdown.
- **Body** — Todo el contenido del archivo después del frontmatter.
- **Link** — Un enlace markdown estándar de un concepto a otro, utilizado
  para expresar relaciones más allá de la jerarquía implícita padre/hijo.
- **Citation** — Un enlace desde un concepto a una fuente externa que
  respalda una afirmación en el body.

---

## 3. Estructura del Bundle

Un bundle es un árbol de directorios con archivos markdown. La estructura de directorios
es independiente del dominio — los productores organizan los conceptos de la manera
que tenga más sentido para el conocimiento que se está capturando.

```
path/to/bundle/
├── index.md                      # Optional. Directory listing for progressive disclosure.
├── log.md                        # Optional. Chronological history of updates.
├── <concept>.md                  # A concept at the bundle root.
└── <subdirectory>/               # Subdirectories organize concepts into groups.
    ├── index.md
    ├── <concept>.md
    └── <subdirectory>/
        └── …
```

Un bundle MAY ser distribuido como:

- Un repositorio git (recomendado — proporciona historial, atribución y diffs).
- Un archivo tarball o zip del directorio.
- Un subdirectorio dentro de un repositorio más grande.

### 3.1 Nombres de archivo reservados

Los siguientes nombres de archivo tienen un significado definido en cualquier nivel de la
jerarquía y MUST NOT ser utilizados para documentos de conceptos:

| Nombre de archivo | Propósito                                              |
|-------------------|--------------------------------------------------------|
| `index.md`        | Listado de directorio. Ver §6.                        |
| `log.md`          | Historial de actualizaciones. Ver §7.                 |

Todos los demás archivos `.md` son documentos de conceptos.

Las etiquetas en sí mismas siguen siendo un concepto de primera clase — ver el campo
`tags` del frontmatter en §4.1. OKF no especifica un formato de archivo separado
para agregar documentos por etiqueta; los productores que deseen una vista de
navegación por etiquetas pueden sintetizar una en el momento del consumo escaneando el frontmatter.

---

## 4. Documentos de Conceptos

Cada concepto es un archivo markdown en UTF-8. Tiene dos partes:

1. Un **bloque de frontmatter YAML**, delimitado por `---` en su propia línea al
   inicio del archivo y un cierre `---` en su propia línea.
2. Un **body en markdown**, que contiene contenido de formato libre.

### 4.1 Frontmatter

```yaml
---
type: <Type name>                  # REQUIRED
title: <Optional display name>
description: <Optional one-line summary>
resource: <Optional canonical URI for the underlying asset>
tags: [<tag>, <tag>, …]            # Optional
timestamp: <ISO 8601 datetime>     # Optional last-modified time
# … other producer-defined key/value pairs
---
```

**Required:**

- `type` — Una cadena corta que identifica el tipo de concepto. Los consumidores
  la utilizan para enrutamiento, filtrado y presentación. Valores de ejemplo:
  `Component`, `API Endpoint`, `Decision Record`, `Process`,
  `Metric`, `Playbook`, `Note`, `Reference`.

  Los valores de type **no** se registran centralmente. Los productores SHOULD elegir
  valores que sean descriptivos y autoexplicativos; los consumidores MUST
  tolerar tipos desconocidos de manera elegante (típicamente tratándolos como
  conceptos genéricos).

**Recomendados (en orden de prioridad):**

- `title` — Nombre para mostrar legible por humanos. Si se omite, los consumidores MAY
  derivar un título a partir del nombre del archivo.
- `description` — Una sola oración que resume el concepto. Utilizada por
  generadores de `index.md`, fragmentos de búsqueda y previsualizaciones.
- `resource` — Una URI que identifica de manera única el activo subyacente que
  el concepto describe. Ausente para conceptos que describen ideas abstractas
  en lugar de recursos físicos.
- `tags` — Una lista YAML de cadenas cortas para categorización transversal.
- `timestamp` — Fecha y hora en formato ISO 8601 del último cambio significativo.

**Extensiones:** Los productores MAY incluir cualquier clave adicional. Los consumidores
SHOULD preservar las claves desconocidas al hacer round-tripping y SHOULD NOT rechazar
documentos con campos no reconocidos.

### 4.2 Body

El body es markdown estándar. Los productores SHOULD favorecer el markdown
estructural — encabezados, listas, tablas, bloques de código delimitados — sobre prosa
de formato libre, ya que la estructura ayuda tanto a la lectura humana como a la
recuperación por agentes.

No hay secciones obligatorias en el body. Los siguientes encabezados de sección tienen
significado **convencional** y SHOULD ser utilizados cuando aplique:

| Encabezado     | Propósito                                              |
|----------------|--------------------------------------------------------|
| `# Schema`     | Descripción estructurada de las columnas/campos de un activo. |
| `# Examples`   | Ejemplos concretos de uso, frecuentemente como bloques de código delimitados. |
| `# Citations`  | Fuentes externas que respaldan afirmaciones en el body. Ver §8. |
| `# Context`    | Información de contexto y motivación detrás del concepto. |
| `# Decision`   | Justificación de una elección o trade-off específico. |
| `# Steps`      | Procedimiento o flujo de trabajo ordenado. |
| `# Links`      | Recursos relacionados, tanto internos como externos. |

### 4.3 Ejemplo: un concepto vinculado a un recurso

```markdown
---
type: API Endpoint
title: User Authentication
description: Handles user login, token issuance, and session management.
resource: https://api.example.com/v2/auth
tags: [auth, security, api]
timestamp: 2026-05-28T14:30:00Z
---

# Schema

| Field          | Type     | Description                              |
|----------------|----------|------------------------------------------|
| `email`        | string   | User's email address.                    |
| `password`     | string   | Hashed password (bcrypt).                |
| `token`        | string   | JWT issued on successful login.          |
| `expires_at`   | datetime | Token expiration timestamp.              |

# Context

This endpoint replaced the legacy `/v1/login` flow. It uses OAuth 2.0
with PKCE for public clients. See [security policy](/policies/auth.md).

# Citations

[1] [OAuth 2.0 for Browser-Based Apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps)
```

### 4.4 Ejemplo: un concepto no vinculado a un recurso

```markdown
---
type: Decision Record
title: Migration to event-driven architecture
description: Decision to adopt event-driven patterns for inter-service communication.
tags: [architecture, backend, events]
timestamp: 2026-04-12T09:00:00Z
---

# Context

The monolithic request-response pattern between services caused cascading
failures during traffic spikes. The team evaluated three alternatives.

# Decision

Adopt an event-driven architecture using a message broker. Services publish
domain events; consumers subscribe to relevant topics.

# Steps

1. Define the event schema registry. See [event schemas](/schemas/events.md).
2. Migrate the [order service](/services/orders.md) as the pilot.
3. Monitor consumer lag and dead-letter queues.
```

---

## 5. Enlaces cruzados

Los conceptos MAY enlazar a otros conceptos utilizando enlaces markdown estándar. Se
soportan dos formas:

### 5.1 Enlaces absolutos (relativos al bundle)

Comienzan con `/`, interpretados en relación a la raíz del bundle.

```markdown
See the [auth endpoint](/api/auth.md) for the login flow.
```

Esta es la forma **recomendada** porque es estable cuando los documentos se
mueven dentro de su subdirectorio.

### 5.2 Enlaces relativos

Rutas relativas estándar de markdown.

```markdown
See the [neighboring concept](./other.md).
```

### 5.3 Semántica de los enlaces

Un enlace del concepto A al concepto B afirma una *relación*. El
tipo específico de relación (padre/hijo, referencia, se-une-con,
depende-de, etc.) se transmite a través de la prosa circundante, no por el enlace
en sí. Los consumidores que construyen una vista de grafo típicamente tratan todos los enlaces como
aristas dirigidas de una relación sin tipo.

Los consumidores MUST tolerar enlaces rotos — un enlace cuyo destino no
existe en el bundle no está malformado; simplemente puede representar
conocimiento aún no escrito.

---

## 6. Archivos Index

Un archivo `index.md` MAY aparecer en cualquier directorio, incluyendo la raíz
del bundle. Enumera el contenido del directorio para soportar la **divulgación
progresiva** — permitiendo que un humano o agente vea lo que está disponible antes
de abrir documentos individuales.

Los archivos index no contienen frontmatter. El body utiliza una o más secciones,
cada una agrupando conceptos bajo un encabezado:

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another Section

* [Subdirectory](subdir/) - short description of the subdirectory
```

Las entradas SHOULD incluir la descripción del frontmatter del concepto enlazado.
Los productores MAY generar `index.md` automáticamente; los consumidores
MAY sintetizar uno al vuelo cuando no haya uno presente.

---

## 7. Archivos Log (opcional)

Un archivo `log.md` MAY aparecer en cualquier nivel de la jerarquía para registrar el
historial de cambios en ese ámbito. El formato es una lista plana de
entradas agrupadas por fecha, con las más recientes primero:

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added new component reference for [Order Service](/services/orders.md).
* **Creation**: Established the [Incident Response Playbook](/playbooks/incident-response.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
* **Update**: Added progressive-disclosure guidelines to the root [index](/index.md).
```

Los encabezados de fecha MUST usar el formato ISO 8601 `YYYY-MM-DD`. Las entradas del log son
prosa; la palabra inicial en negrita (`**Update**`, `**Creation**`,
`**Deprecation**`, etc.) es una convención, no un requisito.

---

## 8. Citas

Cuando el body de un concepto hace afirmaciones basadas en material externo,
esas fuentes SHOULD ser listadas bajo un encabezado `# Citations` al
final del documento, numeradas:

```markdown
# Citations

[1] [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
[2] [Internal architecture decision log](https://wiki.acme.internal/arch/decisions)
```

Los enlaces de citas MAY ser URLs absolutas, rutas relativas al bundle o rutas
hacia un subdirectorio `references/` que replica material externo como
conceptos OKF de primera clase.

---

## 9. Conformidad

Un bundle es **conforme** con OKF v0.1 si:

1. Cada archivo `.md` no reservado en el árbol contiene un bloque de
   frontmatter YAML parseable.
2. Cada bloque de frontmatter contiene un campo `type` no vacío.
3. Cada nombre de archivo reservado (`index.md`, `log.md`) sigue la estructura
   descrita en §6 y §7 respectivamente cuando está presente.

Los consumidores SHOULD tratar todas las demás restricciones como orientación flexible. En
particular, los consumidores MUST NOT rechazar un bundle debido a:

- Campos opcionales de frontmatter faltantes.
- Valores de `type` desconocidos.
- Claves adicionales de frontmatter desconocidas.
- Enlaces cruzados rotos.
- Archivos `index.md` faltantes.

Este modelo de consumo permisivo es intencional: OKF está diseñado para
seguir siendo útil a medida que los bundles crecen, se refactorizan y son parcialmente
generados por agentes.

---

## 10. Relación con otros formatos

OKF es intencionalmente cercano a varios patrones establecidos:

- **Repositorios "wiki" para LLM** que usan markdown + frontmatter como
  bases de conocimiento legibles por agentes.
- **Herramientas de conocimiento personal** como Obsidian y Notion, que usan
  markdown jerárquico con enlaces cruzados.
- **Enfoques de "metadatos como código"** que almacenan metadatos de catálogo
  junto al código fuente en lugar de en un registro separado.

OKF se diferencia principalmente en estar **especificado** — fijando el conjunto reducido
de reglas necesarias para la interoperabilidad sin dictar herramientas.

---

## 11. Versionado

Este documento especifica la versión **0.1** de OKF. Las revisiones futuras serán
versionadas en la forma `<major>.<minor>`:

- Un incremento de versión **minor** introduce adiciones compatibles hacia atrás
  (nuevos campos opcionales, nuevos encabezados de sección convencionales).
- Un incremento de versión **major** puede hacer cambios incompatibles (renombrar campos
  obligatorios, cambiar nombres de archivos reservados).

Los bundles MAY declarar la versión de OKF a la que apuntan incluyendo
`okf_version: "0.1"` en un bloque de frontmatter del `index.md` en la raíz del bundle (el
único lugar donde se permite frontmatter en un `index.md`). Los consumidores que
no comprendan la versión declarada SHOULD intentar un consumo de mejor esfuerzo
en lugar de rechazar el bundle.

---

## Apéndice A — Ejemplo mínimal de bundle

```
my_bundle/
├── index.md
├── services/
│   ├── index.md
│   ├── orders.md
│   └── auth.md
├── decisions/
│   ├── index.md
│   └── event-driven.md
└── playbooks/
    ├── index.md
    └── incident-response.md
```

`services/orders.md`:

```markdown
---
type: Component
title: Order Service
description: Manages order lifecycle from creation to fulfillment.
resource: https://github.com/acme/orders-service
tags: [backend, orders]
timestamp: 2026-05-28T00:00:00Z
---

The order service handles creation, payment, and fulfillment workflows.
It publishes events consumed by [auth](/services/auth.md) and
documented in the [event-driven decision](/decisions/event-driven.md).
```

`decisions/event-driven.md`:

```markdown
---
type: Decision Record
title: Event-driven architecture
description: Decision to adopt event-driven communication between services.
tags: [architecture, events]
timestamp: 2026-05-28T00:00:00Z
---

# Context

Cascading failures during peak traffic motivated a move away from
synchronous inter-service calls.

# Decision

Adopt event-driven architecture with a message broker. The
[order service](/services/orders.md) was the first to migrate.
```
