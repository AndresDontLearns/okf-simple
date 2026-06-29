from __future__ import annotations


def _fallback(children: list[tuple[str, str]]) -> str:
    titles = ", ".join(t for t, _ in children if t) or "no titled entries"
    return f"Contains {len(children)} entries: {titles}."


def synthesize_description(
    rel_path: str,
    children: list[tuple[str, str]],
) -> str:
    if not children:
        return ""
    return _fallback(children)
