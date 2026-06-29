# OKF Simple

**v0.1.0** — Implementación de referencia de [Open Knowledge Format (OKF)](SPEC.md).

OKF es un formato abierto para representar conocimiento como directorios de
archivos markdown con frontmatter YAML. Este paquete provee un CLI y una
librería Python para crear, leer, escribir y visualizar bundles OKF.

## Qué incluye

- **CLI** con comandos `init`, `add`, `read`, `write`, `index` y `viz`.
- **Librería Python** importable (`okf.read_existing_doc`, `okf.write_concept_doc`, etc.).
- **Visualizador HTML** autocontenido — genera un grafo interactivo del bundle sin backend.
- **Skill de agente** (`.agents/skills/okf_simple/SKILL.md`) para que agentes de IA operen bundles OKF.

## Inicio rápido

### 1. Instalar

Requiere **Python 3.11+**.

```bash
git clone https://github.com/tu-usuario/okf-simple.git
cd okf-simple
pip install -e .
```

### 2. Crear un bundle

```bash
okf init bundles/mi_proyecto
```

Esto crea el directorio y un `index.md` raíz.

### 3. Agregar conceptos

```bash
okf add bundles/mi_proyecto servicios/auth --type Component --title "Auth Service"
okf add bundles/mi_proyecto servicios/orders --type Component
```

### 4. Escribir contenido

```bash
okf write bundles/mi_proyecto servicios/auth \
  --frontmatter '{"type":"Component","title":"Auth Service","description":"Servicio de autenticación OAuth2.","tags":["backend","auth"]}' \
  --body "Gestiona la autenticación y autorización de usuarios.\n\n# Context\n\nImplementado sobre OAuth2 con refresh tokens."
```

### 5. Leer un concepto

```bash
okf read bundles/mi_proyecto servicios/auth
```

Retorna el documento como JSON con `frontmatter` y `body`.

### 6. Regenerar índices

```bash
okf index bundles/mi_proyecto
```

Reconstruye los archivos `index.md` en cada directorio del bundle.

### 7. Generar visualización

```bash
okf viz bundles/mi_proyecto
```

Genera `bundles/mi_proyecto/viz.html` — un archivo HTML interactivo con el
grafo de conceptos y sus enlaces cruzados. Ábrelo en cualquier navegador.

## Usar como librería Python

```python
import okf

okf.set_context("bundles/mi_proyecto")

# Escribir un concepto
okf.write_concept_doc(
    "servicios/auth",
    {"type": "Component", "title": "Auth Service", "description": "OAuth2 auth."},
    "Gestiona autenticación y autorización.",
)

# Leer un concepto
doc = okf.read_existing_doc("servicios/auth")
print(doc["frontmatter"]["title"])  # "Auth Service"

# Regenerar índices
okf.regenerate_indexes("bundles/mi_proyecto")

# Generar visualización
okf.generate_visualization("bundles/mi_proyecto", "bundles/mi_proyecto/viz.html")
```

## Usar en un proyecto propio

Para integrar OKF como sistema de documentación de conocimiento en tu proyecto:

1. **Clona el repositorio** dentro de tu proyecto (por ejemplo como submódulo o en una carpeta de herramientas):

   ```bash
   git clone https://github.com/tu-usuario/okf-simple.git tools/okf-simple
   pip install -e tools/okf-simple
   ```

   O como submódulo de git:

   ```bash
   git submodule add https://github.com/tu-usuario/okf-simple.git tools/okf-simple
   pip install -e tools/okf-simple
   ```

2. **Crea un bundle** en tu repositorio:

   ```bash
   okf init docs/knowledge
   ```

3. **Documenta conceptos** de tu proyecto (servicios, APIs, decisiones, procesos):

   ```bash
   okf add docs/knowledge apis/users --type "API Endpoint"
   okf add docs/knowledge decisions/event-driven --type "Decision Record"
   ```

4. **Commitea el bundle** junto con tu código — se versiona con git como cualquier archivo.

5. **Genera la visualización** para navegación interactiva:

   ```bash
   okf viz docs/knowledge
   ```

### Integración con agentes

Si tu proyecto usa agentes de IA, copia la skill en
`.agents/skills/okf_simple/SKILL.md` para que el agente pueda crear y
enriquecer conceptos OKF de forma autónoma. La skill documenta el formato
de documentos, el flujo de trabajo y las reglas de operación.

## Estructura de un bundle OKF

```
mi_bundle/
├── index.md              # Índice raíz (autogenerado)
├── servicios/
│   ├── index.md          # Índice del directorio
│   ├── auth.md           # Concepto: frontmatter YAML + body markdown
│   └── orders.md
└── viz.html              # Visualización (opcional)
```

Cada concepto es un archivo markdown con frontmatter YAML:

```markdown
---
type: Component
title: Auth Service
description: Servicio de autenticación y autorización OAuth2.
resource: https://github.com/acme/auth-service
tags: [backend, auth, oauth2]
---

Gestiona la autenticación de usuarios mediante OAuth2 con refresh tokens.

# Schema

| Campo       | Tipo   | Descripción           |
|-------------|--------|-----------------------|
| `user_id`   | string | Identificador único   |
| `token`     | string | JWT de acceso         |

# Context

Extraído del monolito durante la migración a microservicios.
```

## Tests

```bash
pip install -e .[dev]
pytest
```

## Especificación

La especificación completa del formato está en [SPEC.md](SPEC.md).
