from __future__ import annotations

from okf.tools.bundle_tools import read_existing_doc, write_concept_doc
from okf.tools.web_tools import fetch_url
from okf.bundle.index import regenerate_indexes
from okf.viewer.generator import generate_visualization
from okf.tools.context import (
    set_context,
    get_context,
    set_web_state,
    get_web_state,
    clear_web_state,
    is_web_pass,
)

__version__ = "0.1.0"


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
    "read_existing_doc",
    "write_concept_doc",
    "fetch_url",
    "regenerate_indexes",
    "generate_visualization",
    "init_web_state",
    "set_context",
    "get_context",
    "set_web_state",
    "get_web_state",
    "clear_web_state",
    "is_web_pass",
]
