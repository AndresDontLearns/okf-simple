---
name: okf_simple
description: Crear, enriquecer y gestionar bundles de conocimiento en Open Knowledge Format (OKF).
---

# OKF Simple — Skill de Agente

OKF es un formato abierto para representar conocimiento como un directorio
de archivos markdown con frontmatter YAML. Esta skill permite a cualquier
agente crear, leer, escribir y mantener bundles OKF usando el CLI `okf`.

---

## Comandos CLI disponibles

Todos los comandos retornan JSON en stdout.

### Crear un bundle

```bash
okf init <path>
```

Crea el directorio y un `index.md` raíz si no existe.

### Agregar un concepto vacío

```bash
okf add <bundle> <concept_id> [--type <Type>] [--title <Title>]
```

- `concept_id` es una ruta separada por `/` (ej: `services/auth`).
- `--type` define el tipo de concepto (default: `Note`).
- `--title` es opcional; se deriva del concept_id si se omite.

### Leer un concepto existente

```bash
okf read <bundle> <concept_id>
```

Retorna `{"frontmatter": {...}, "body": "..."}` o `null` si no existe.
Úsalo **siempre** antes de escribir para no sobreescribir contenido previo.

### Escribir / actualizar un concepto

```bash
okf write <bundle> <concept_id> --frontmatter <json> --body <markdown>
```

- `--frontmatter`: string JSON o ruta a archivo JSON.
- `--body`: string markdown o ruta a archivo.
- Valida que el frontmatter incluya al menos `type`.
- Retorna `{"path": "...", "bytes": N}` o `{"error": "..."}` si falla.

### Regenerar índices

```bash
okf index <bundle>
```

Reconstruye los archivos `index.md` en cada directorio del bundle.

### Generar visualización

```bash
okf viz <bundle> [--out <path>] [--name <name>]
```

Genera un archivo HTML autocontenido con un grafo interactivo de los
conceptos y sus enlaces cruzados.

---

## Formato de documentos OKF

Cada concepto es un archivo markdown con dos partes: un bloque de
frontmatter YAML delimitado por `---`, y un body en markdown.

### Frontmatter (claves requeridas)

- `type`: tipo de concepto. Valores típicos: `Component`, `API Endpoint`,
  `Decision Record`, `Note`, `Playbook`, `Reference`, `Metric`, `Process`.
  No hay una taxonomía fija — usa el valor que mejor describa el concepto.
- `title`: nombre corto y legible para humanos.
- `description`: **una sola oración** que resuma el concepto. Se usa
  textualmente en los `index.md` generados, así que debe ser concisa e
  informativa.
- `timestamp`: omitir — la herramienta completa la hora UTC actual
  automáticamente. Si necesitas un valor específico, usa ISO 8601.

### Frontmatter (claves recomendadas)

- `resource`: URI del activo subyacente que el concepto describe (un repo,
  un endpoint, una tabla). Omitir para conceptos abstractos.
- `tags`: lista YAML de etiquetas de búsqueda inferidas del contenido.

### Secciones del body (en este orden)

1. **Descripción en prosa** (1–3 párrafos) — qué es, qué representa, cómo
   se usa.
2. **`# Schema`** — si el concepto tiene campos o estructura, un resumen
   legible. Omitir si no aplica.
3. **`# Context`** — motivación, historia y contexto detrás del concepto.
4. **`# Examples`** — de 1 a 3 ejemplos concretos de uso.
5. **`# Citations`** — fuentes externas numeradas:
   ```
   [1] [Source Title](https://example.com/...)
   [2] [Another Source](https://example.com/...)
   ```
   Incluir el valor de `resource` como primera entrada cuando esté presente.
   No inventar URLs — citar únicamente fuentes conocidas.

### Ejemplo de documento

```markdown
---
type: Component
title: Order Service
description: Manages order lifecycle from creation to fulfillment.
resource: https://github.com/acme/orders-service
tags: [backend, orders, events]
---

The order service handles creation, payment, and fulfillment workflows.
It publishes domain events consumed by downstream services.

# Schema

| Field        | Type     | Description                    |
|--------------|----------|--------------------------------|
| `order_id`   | string   | Unique order identifier (UUID) |
| `status`     | enum     | pending, paid, shipped, closed |
| `created_at` | datetime | Order creation timestamp       |

# Context

Originally part of the monolith, extracted as a standalone service during
the migration to event-driven architecture.

# Examples

Create a new order via the API:

    POST /api/v2/orders
    {"items": [{"sku": "ABC-123", "qty": 2}]}

# Citations

[1] [Order Service repo](https://github.com/acme/orders-service)
```

---

## Flujo de trabajo de enriquecimiento

Para enriquecer un concepto, sigue esta secuencia:

1. **Leer primero**: `okf read <bundle> <concept_id>`. Si ya existe, úsalo
   como base — refina en lugar de reescribir.
2. **Componer el documento** siguiendo las convenciones de frontmatter y
   secciones del body descritas arriba.
3. **Escribir**: `okf write <bundle> <concept_id> --frontmatter '...' --body '...'`.
4. **Regenerar índices**: `okf index <bundle>` al terminar un lote de
   escrituras.

---

## Reglas de operación

1. **Leer antes de escribir.** Nunca sobreescribas un documento sin leer
   su contenido actual primero.

2. **Enlaces cruzados relativos.** Enlaza conceptos usando rutas relativas
   al directorio del documento actual. Nunca uses rutas absolutas con `/`.
   - Concepto hermano: `[users](users.md)`
   - Concepto en otro directorio: `[event parameters](../references/event_parameters.md)`
   - Solo enlaza conceptos que sepas que existen.
   - Un enlace por mención por sección es suficiente.
   - No enlaces desde encabezados ni bloques de código.

3. **Integridad de aumentación.** Al actualizar un documento existente:
   - Preserva todas las claves de frontmatter existentes (`type`, `title`,
     `resource`) — cópialas textualmente al nuevo diccionario.
   - Preserva todos los encabezados `#` existentes, en el mismo orden.
   - No elimines campos del esquema ni citas. La herramienta rechazará
     la escritura si detecta pérdida de contenido.
   - Para `tags`, fusiona los existentes con los nuevos.
   - Puedes extender prosa, agregar viñetas a listas, y agregar nuevas
     secciones **después** de las existentes.

4. **No inventar.** No cites URLs que no conozcas. No inventes datos que
   no estén en los metadatos fuente. No inventes destinos de enlaces.

5. **Markdown limpio.** Sin preámbulos, disculpas ni narración de
   razonamiento en los documentos. El body debe ser consumible directamente
   por humanos y agentes.
