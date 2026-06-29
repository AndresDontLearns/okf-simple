from __future__ import annotations

from pathlib import Path

import pytest

from okf.tools.bundle_tools import write_concept_doc
from okf.tools.context import set_context


def _set_ctx(tmp_path: Path) -> None:
    set_context(tmp_path)


def _good_frontmatter(**overrides):
    fm = {
        "type": "Component",
        "title": "Users",
        "description": "A component for users.",
        "tags": ["users"],
    }
    fm.update(overrides)
    return fm


def _doc_body(fields: list[str], citations: list[str]) -> str:
    schema_lines = "\n".join(f"- `{f}` STRING: desc" for f in fields)
    cite_lines = "\n".join(citations)
    return f"Prose.\n\n# Schema\n{schema_lines}\n\n# Citations\n{cite_lines}\n"


def test_write_succeeds_when_no_existing_doc(tmp_path):
    _set_ctx(tmp_path)
    result = write_concept_doc(
        "tables/users",
        _good_frontmatter(),
        _doc_body(["id", "name"], ["[1] [Src](https://src)"]),
    )
    assert "error" not in result
    assert (tmp_path / "tables" / "users.md").exists()


def test_rejects_schema_shrinkage(tmp_path):
    _set_ctx(tmp_path)
    write_concept_doc(
        "tables/users",
        _good_frontmatter(),
        _doc_body(["id", "name", "email", "created_at"], ["[1] [Src](https://src)"]),
    )
    result = write_concept_doc(
        "tables/users",
        _good_frontmatter(),
        _doc_body(["id", "name"], ["[1] [Src](https://src)", "[2] [Web](https://web)"]),
    )
    assert "error" in result
    assert "missing 2" in result["error"]
    assert "`email`" in result["error"]
    assert "`created_at`" in result["error"]


def test_rejects_citation_shrinkage(tmp_path):
    _set_ctx(tmp_path)
    write_concept_doc(
        "tables/users",
        _good_frontmatter(),
        _doc_body(["id"], ["[1] [Src](https://src)", "[2] [Other](https://other)"]),
    )
    result = write_concept_doc(
        "tables/users",
        _good_frontmatter(),
        _doc_body(["id"], ["[1] [Web](https://web)"]),
    )
    assert "error" in result
    assert "had 2 entries" in result["error"]


def test_allows_augmentation_with_new_section(tmp_path):
    _set_ctx(tmp_path)
    write_concept_doc(
        "tables/users",
        _good_frontmatter(),
        _doc_body(["id", "name"], ["[1] [Src](https://src)"]),
    )
    augmented = (
        "Prose.\n\n# Schema\n- `id` STRING: desc\n- `name` STRING: desc\n\n"
        "# Metrics\n- [DAU](/references/metrics/dau.md) — count distinct id\n\n"
        "# Citations\n[1] [Src](https://src)\n[2] [Web](https://web)\n"
    )
    result = write_concept_doc("tables/users", _good_frontmatter(), augmented)
    assert "error" not in result
