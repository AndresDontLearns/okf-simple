from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from reference_agent import (
    list_concepts,
    read_concept_raw,
    sample_rows,
    read_existing_doc,
    write_concept_doc,
    fetch_url,
    regenerate_indexes,
    generate_visualization,
    init_context,
    init_web_state,
    set_context,
)
from reference_agent.sources.base import Source

DEFAULT_MODEL = "gemini-flash-latest"


class DummySource(Source):
    def list_concepts(self):
        return []

    def read_concept(self, ref):
        return {}


def _load_string_or_file(val: str) -> str:
    try:
        p = Path(val)
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8")
    except Exception:
        pass
    return val


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="reference-agent")
    sub = p.add_subparsers(dest="command", required=True)

    # 1. list-concepts
    lc = sub.add_parser("list-concepts", help="List concepts from a source.")
    lc.add_argument("--source", choices=["bq"], required=True)
    lc.add_argument("--dataset", required=True)
    lc.add_argument("--billing-project")

    # 2. read-concept
    rc = sub.add_parser("read-concept", help="Read raw metadata for a concept.")
    rc.add_argument("--source", choices=["bq"], required=True)
    rc.add_argument("--dataset", required=True)
    rc.add_argument("--concept", required=True)
    rc.add_argument("--billing-project")

    # 3. sample-rows
    sr = sub.add_parser("sample-rows", help="Sample rows for a concept.")
    sr.add_argument("--source", choices=["bq"], required=True)
    sr.add_argument("--dataset", required=True)
    sr.add_argument("--concept", required=True)
    sr.add_argument("--n", type=int, default=5)
    sr.add_argument("--billing-project")

    # 4. read-doc
    rd = sub.add_parser("read-doc", help="Read existing doc from bundle.")
    rd.add_argument("--bundle", required=True, type=Path)
    rd.add_argument("--concept", required=True)

    # 5. write-doc
    wd = sub.add_parser("write-doc", help="Write/update a concept doc in bundle.")
    wd.add_argument("--bundle", required=True, type=Path)
    wd.add_argument("--concept", required=True)
    wd.add_argument("--frontmatter", required=True)
    wd.add_argument("--body", required=True)

    # 6. fetch-url
    fu = sub.add_parser("fetch-url", help="Fetch a single web page content.")
    fu.add_argument("--url", required=True)
    fu.add_argument("--seeds")
    fu.add_argument("--max-pages", type=int)

    # 7. regenerate-indexes
    ri = sub.add_parser("regenerate-indexes", help="Regenerate indexes in bundle.")
    ri.add_argument("--bundle", required=True, type=Path)
    ri.add_argument("--model", default=DEFAULT_MODEL)

    # 8. visualize
    viz = sub.add_parser("visualize", help="Generate HTML graph view.")
    viz.add_argument("--bundle", required=True, type=Path)
    viz.add_argument("--out", type=Path, default=None)
    viz.add_argument("--name", default=None)

    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )
    # Quiet chatty third-party loggers regardless of mode.
    for noisy in ("google", "google_genai", "google_adk", "urllib3", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    try:
        if args.command == "list-concepts":
            init_context(args.source, args.dataset, Path.cwd(), billing_project=args.billing_project)
            concepts = list_concepts()
            print(json.dumps(concepts, indent=2, ensure_ascii=False))
            return 0

        elif args.command == "read-concept":
            init_context(args.source, args.dataset, Path.cwd(), billing_project=args.billing_project)
            concept_data = read_concept_raw(args.concept)
            print(json.dumps(concept_data, indent=2, ensure_ascii=False))
            return 0

        elif args.command == "sample-rows":
            init_context(args.source, args.dataset, Path.cwd(), billing_project=args.billing_project)
            sampled = sample_rows(args.concept, n=args.n)
            print(json.dumps(sampled, indent=2, ensure_ascii=False))
            return 0

        elif args.command == "read-doc":
            set_context(DummySource(), args.bundle)
            result = read_existing_doc(args.concept)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        elif args.command == "write-doc":
            set_context(DummySource(), args.bundle)
            # Handle frontmatter loading (could be JSON string or file path containing JSON)
            fm_str = _load_string_or_file(args.frontmatter)
            try:
                frontmatter = json.loads(fm_str)
            except Exception as e:
                print(json.dumps({"error": f"Failed to parse frontmatter as JSON: {e}"}, indent=2), file=sys.stderr)
                return 1

            body = _load_string_or_file(args.body)
            result = write_concept_doc(args.concept, frontmatter, body)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if "error" in result:
                return 1
            return 0

        elif args.command == "fetch-url":
            if args.seeds or args.max_pages is not None:
                seeds_list = []
                if args.seeds:
                    seeds_list = [s.strip() for s in args.seeds.split(",") if s.strip()]
                max_pages = args.max_pages if args.max_pages is not None else 100
                init_web_state(seeds=seeds_list, max_pages=max_pages)
            result = fetch_url(args.url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if "error" in result:
                return 1
            return 0

        elif args.command == "regenerate-indexes":
            regenerate_indexes(args.bundle, model=args.model)
            print(json.dumps({"status": "success", "message": f"Indexes regenerated for {args.bundle}"}, indent=2))
            return 0

        elif args.command == "visualize":
            out = args.out or (args.bundle / "viz.html")
            stats = generate_visualization(args.bundle, out, bundle_name=args.name)
            print(json.dumps({
                "status": "success",
                "message": f"Visualization generated at {out}",
                "stats": stats
            }, indent=2))
            return 0

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1

    return 1
