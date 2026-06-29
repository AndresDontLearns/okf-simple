# Eliminar fetch_url y delegar web crawl a Claude Code

## Contexto

La tool `fetch_url` en `src/okf/tools/web_tools.py` duplica capacidad que
Claude Code ya tiene nativamente con `WebFetch`/`WebSearch`. Además, el
`WebState` (budget, visited, depth tracking) vive en memoria del proceso
Python, lo que lo hace incompatible con invocaciones CLI independientes
— cada `okf fetch-url` pierde el estado.

La lógica de decisión del crawl (qué enlaces seguir, cuándo parar, qué
es relevante) ya está descrita en
`src/okf/prompts/web_ingestion_instruction.md` como instrucciones para un
agente. Claude Code puede ejecutar ese juicio directamente usando sus
herramientas nativas.

## Qué eliminar

1. **`src/okf/tools/web_tools.py`** — el módulo completo.
2. **`src/okf/web/`** — el paquete `fetcher.py` y su `__init__.py`.
3. **`src/okf/tools/context.py`** — las funciones y clases relacionadas con
   web state: `WebState`, `set_web_state`, `get_web_state`, `clear_web_state`,
   `is_web_pass`. Mantener `ToolContext`, `set_context`, `get_context`.
4. **`src/okf/cli.py`** — el subcomando `fetch-url` y el import de
   `init_web_state`/`fetch_url`.
5. **`src/okf/__init__.py`** — los exports relacionados con web:
   `fetch_url`, `init_web_state`, `set_web_state`, `get_web_state`,
   `clear_web_state`, `is_web_pass`.
6. **`pyproject.toml`** — la dependencia `markdownify` (verificar que no se
   use en otro lugar antes de quitarla).
7. **`tests/test_web_fetcher.py`** y **`tests/test_web_tools.py`**.
8. **`.agents/skills/okf_simple/SKILL.md`** — eliminar la referencia a
   `fetch_url` de la lista de herramientas y del paso 4 del flujo de trabajo.

## Qué conservar / mover

- **`src/okf/prompts/web_ingestion_instruction.md`** — mantenerlo como
  instrucción para Claude Code. Adaptarlo para que referencie `WebFetch` en
  lugar de `fetch_url`, y `okf write` en lugar de `write_concept_doc()`.
- **La validación de augmentation** en `bundle_tools.py` (`is_web_pass`
  checks en `write_concept_doc`) — evaluar si se elimina o se reemplaza por
  un flag explícito `--augment` en el CLI.

## Qué gana el proyecto

- Menos código que mantener (~300 líneas entre web_tools, fetcher, WebState).
- El CLI queda stateless y enfocado en operaciones de bundle.
- El web crawl se beneficia de las capacidades nativas de Claude Code
  (manejo de rate limits, headers, rendering JS si aplica).
