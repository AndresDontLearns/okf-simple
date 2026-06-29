from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolContext:
    bundle_root: Path


_ctx: ToolContext | None = None


def set_context(bundle_root: Path) -> None:
    global _ctx
    _ctx = ToolContext(bundle_root=Path(bundle_root))


def get_context() -> ToolContext:
    if _ctx is None:
        raise RuntimeError(
            "Tool context not set. Call set_context() before invoking the agent."
        )
    return _ctx
