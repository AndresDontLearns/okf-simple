from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_string_or_file(val: str) -> str:
    """If val is a path to an existing file, read it; otherwise return val as-is."""
    try:
        p = Path(val)
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8")
    except Exception:
        pass
    return val


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="okf", description="Open Knowledge Format CLI")
    sub = p.add_subparsers(dest="command", required=True)

    # init
    init_p = sub.add_parser("init", help="Create a new OKF bundle.")
    init_p.add_argument("path", type=Path, help="Path for the new bundle directory.")

    # add
    add_p = sub.add_parser("add", help="Add a new concept to a bundle.")
    add_p.add_argument("bundle", type=Path, help="Bundle directory.")
    add_p.add_argument("concept_id", help="Concept ID (slash-separated path, e.g. 'notes/meeting-2024').")
    add_p.add_argument("--type", default="Note", dest="concept_type", help="Concept type (default: Note).")
    add_p.add_argument("--title", default=None, help="Display title.")

    # read
    read_p = sub.add_parser("read", help="Read an existing concept.")
    read_p.add_argument("bundle", type=Path)
    read_p.add_argument("concept_id")

    # write
    write_p = sub.add_parser("write", help="Write/update a concept document.")
    write_p.add_argument("bundle", type=Path)
    write_p.add_argument("concept_id")
    write_p.add_argument("--frontmatter", required=True, help="JSON string or path to JSON file.")
    write_p.add_argument("--body", required=True, help="Markdown body string or path to file.")

    # index
    idx_p = sub.add_parser("index", help="Regenerate index.md files in a bundle.")
    idx_p.add_argument("bundle", type=Path)

    # viz
    viz_p = sub.add_parser("viz", help="Generate HTML graph visualization.")
    viz_p.add_argument("bundle", type=Path)
    viz_p.add_argument("--out", type=Path, default=None)
    viz_p.add_argument("--name", default=None)

    # fetch-url
    fetch_p = sub.add_parser("fetch-url", help="Fetch and extract content from a web page.")
    fetch_p.add_argument("--url", required=True)
    fetch_p.add_argument("--seeds")
    fetch_p.add_argument("--max-pages", type=int)

    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for noisy in ("urllib3", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    try:
        if args.command == "init":
            bundle_path = Path(args.path)
            bundle_path.mkdir(parents=True, exist_ok=True)
            index_path = bundle_path / "index.md"
            if not index_path.exists():
                index_path.write_text(
                    f"# {bundle_path.resolve().name}\n\nKnowledge bundle.\n",
                    encoding="utf-8",
                )
            print(json.dumps({"status": "success", "path": str(bundle_path)}, indent=2))
            return 0

        elif args.command == "add":
            from okf.tools.context import set_context
            from okf.tools.bundle_tools import write_concept_doc

            set_context(args.bundle)
            title = args.title or args.concept_id.split("/")[-1].replace("-", " ").replace("_", " ").title()
            fm = {
                "type": args.concept_type,
                "title": title,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            result = write_concept_doc(args.concept_id, fm, "")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1 if "error" in result else 0

        elif args.command == "read":
            from okf.tools.context import set_context
            from okf.tools.bundle_tools import read_existing_doc

            set_context(args.bundle)
            result = read_existing_doc(args.concept_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        elif args.command == "write":
            from okf.tools.context import set_context
            from okf.tools.bundle_tools import write_concept_doc

            set_context(args.bundle)
            fm_str = _load_string_or_file(args.frontmatter)
            try:
                frontmatter = json.loads(fm_str)
            except Exception as e:
                print(json.dumps({"error": f"Failed to parse frontmatter JSON: {e}"}, indent=2), file=sys.stderr)
                return 1
            body = _load_string_or_file(args.body)
            result = write_concept_doc(args.concept_id, frontmatter, body)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1 if "error" in result else 0

        elif args.command == "index":
            from okf.bundle.index import regenerate_indexes

            regenerate_indexes(args.bundle)
            print(json.dumps({"status": "success", "message": f"Indexes regenerated for {args.bundle}"}, indent=2))
            return 0

        elif args.command == "viz":
            from okf.viewer.generator import generate_visualization

            out = args.out or (args.bundle / "viz.html")
            stats = generate_visualization(args.bundle, out, bundle_name=args.name)
            print(json.dumps({"status": "success", "path": str(out), "stats": stats}, indent=2))
            return 0

        elif args.command == "fetch-url":
            from okf import init_web_state, fetch_url

            if args.seeds or args.max_pages is not None:
                seeds_list = [s.strip() for s in args.seeds.split(",") if s.strip()] if args.seeds else []
                max_pages = args.max_pages if args.max_pages is not None else 100
                init_web_state(seeds=seeds_list, max_pages=max_pages)
            result = fetch_url(args.url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1 if "error" in result else 0

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1

    return 1
