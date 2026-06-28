from __future__ import annotations

from pathlib import Path

from reference_agent.tools.source_tools import list_concepts, read_concept_raw, sample_rows
from reference_agent.tools.bundle_tools import read_existing_doc, write_concept_doc
from reference_agent.tools.web_tools import fetch_url
from reference_agent.bundle.index import regenerate_indexes
from reference_agent.viewer.generator import generate_visualization
from reference_agent.tools.context import (
    set_context,
    get_context,
    set_web_state,
    get_web_state,
    clear_web_state,
    is_web_pass,
)

__version__ = "0.1.0"


def init_context(
    source_type: str,
    dataset: str,
    bundle_root: str | Path,
    billing_project: str | None = None,
) -> None:
    from reference_agent.sources.bigquery import BigQuerySource
    source = BigQuerySource(dataset, billing_project)
    set_context(source, Path(bundle_root))


def init_web_state(
    seeds: list[str] | None,
    max_pages: int,
    allowed_hosts: set[str] | list[str] | None = None,
    allowed_path_prefixes: list[str] | None = None,
    denied_path_substrings: list[str] | None = None,
    max_depth: int = 2,
) -> None:
    from urllib.parse import urlparse
    seeds_list = list(seeds or [])
    if allowed_hosts is None:
        allowed_hosts = {urlparse(s).netloc for s in seeds_list if urlparse(s).netloc}
    set_web_state(
        allowed_hosts=set(allowed_hosts),
        max_pages=max_pages,
        seeds=seeds_list,
        allowed_path_prefixes=allowed_path_prefixes,
        denied_path_substrings=denied_path_substrings,
        max_depth=max_depth,
    )


__all__ = [
    "list_concepts",
    "read_concept_raw",
    "sample_rows",
    "read_existing_doc",
    "write_concept_doc",
    "fetch_url",
    "regenerate_indexes",
    "generate_visualization",
    "init_context",
    "init_web_state",
    "set_context",
    "get_context",
    "set_web_state",
    "get_web_state",
    "clear_web_state",
    "is_web_pass",
]
