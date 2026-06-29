# OKF Simple

Implementación de referencia de Open Knowledge Format (OKF) — un formato
abierto para representar conocimiento como directorios de markdown con
frontmatter YAML.

## Setup

```bash
pip install -e .
```

## Tests

```bash
pytest
```

## CLI

El CLI se ejecuta como módulo de Python, **no** como ejecutable instalado:

```bash
python src/okf <command> [args...]
```

Ejemplos:

```bash
python src/okf init bundles/mi_bundle
python src/okf add bundles/mi_bundle notes/idea --type Note
python src/okf read bundles/mi_bundle notes/idea
python src/okf write bundles/mi_bundle notes/idea --frontmatter '{"type":"Note","title":"Idea"}' --body "Contenido"
python src/okf index bundles/mi_bundle
python src/okf viz bundles/mi_bundle
```

## Skill de agente

Las instrucciones completas para operar bundles OKF están en
`.agents/skills/okf_simple/SKILL.md`.
