from __future__ import annotations

import json
import re
from pathlib import Path
from textwrap import dedent

import pytest

from okf.viewer.generator import generate_visualization


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body).lstrip(), encoding="utf-8")


def _make_bundle(root: Path) -> None:
    _write(
        root / "categories" / "my_category.md",
        """
        ---
        type: Category
        title: My category
        description: A test category.
        resource: https://example.com/category
        tags: [test]
        timestamp: '2026-05-28T00:00:00+00:00'
        ---
        Parent category for [users](../components/users.md).
        """,
    )
    _write(
        root / "components" / "users.md",
        """
        ---
        type: Component
        title: Users
        description: User profiles.
        resource: https://example.com/users
        tags: [users]
        timestamp: '2026-05-28T00:00:00+00:00'
        ---
        Joinable with [events](events.md) and see [DAU](../references/metrics/dau.md).
        """,
    )
    _write(
        root / "components" / "events.md",
        """
        ---
        type: Component
        title: Events
        description: User events.
        resource: https://example.com/events
        tags: [events]
        timestamp: '2026-05-28T00:00:00+00:00'
        ---
        See [users](users.md).
        """,
    )
    _write(
        root / "references" / "metrics" / "dau.md",
        """
        ---
        type: Reference
        title: Daily active users
        description: DAU metric.
        resource: https://example.com/dau
        tags: [metric]
        timestamp: '2026-05-28T00:00:00+00:00'
        ---
        COUNT(DISTINCT user_id) per day.
        """,
    )
    _write(root / "index.md", "# My Bundle\n- components/users\n- components/events\n")


def _extract_bundle_data(html: str) -> dict:
    m = re.search(r"window\.BUNDLE\s*=\s*(\{.*?\});", html, re.DOTALL)
    assert m, "BUNDLE JSON not found in generated HTML"
    return json.loads(m.group(1))


def test_generate_visualization_writes_html(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_bundle(bundle)
    out = tmp_path / "viz.html"
    stats = generate_visualization(bundle, out, bundle_name="My Bundle")

    assert out.exists()
    assert stats["concepts"] == 4
    assert stats["bytes"] > 0
    html = out.read_text(encoding="utf-8")
    assert "<title>OKF Bundle Viewer</title>" in html
    assert "cytoscape" in html.lower()
    assert "marked" in html.lower()
    assert '"My Bundle"' in html


def test_index_md_is_not_a_concept(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    ids = {n["data"]["id"] for n in data["nodes"]}
    assert "index" not in ids
    assert ids == {
        "categories/my_category",
        "components/users",
        "components/events",
        "references/metrics/dau",
    }


def test_cross_links_become_edges(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    pairs = {(e["data"]["source"], e["data"]["target"]) for e in data["edges"]}
    assert ("categories/my_category", "components/users") in pairs
    assert ("components/users", "components/events") in pairs
    assert ("components/users", "references/metrics/dau") in pairs
    assert ("components/events", "components/users") in pairs


def test_missing_link_targets_are_skipped(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _write(
        bundle / "components" / "lonely.md",
        """
        ---
        type: Component
        title: Lonely
        description: Has a dangling link.
        timestamp: '2026-05-28T00:00:00+00:00'
        ---
        Links to [missing](missing.md).
        """,
    )
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))
    assert data["edges"] == []
    assert len(data["nodes"]) == 1


def test_nodes_have_colors_for_all_types(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _make_bundle(bundle)
    out = tmp_path / "viz.html"
    generate_visualization(bundle, out)
    data = _extract_bundle_data(out.read_text(encoding="utf-8"))

    node_types = {n["data"]["type"] for n in data["nodes"]}
    assert node_types == set(data["palette"].keys())

    for node in data["nodes"]:
        color = node["data"]["color"]
        assert re.match(r"^#[0-9a-f]{6}$", color), f"Invalid color: {color}"


def test_raises_when_bundle_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        generate_visualization(tmp_path / "nope", tmp_path / "viz.html")
