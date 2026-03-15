#!/usr/bin/env python3
"""Load deterministic handoff context for the Tapestry synthesis skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _src.store import KnowledgeBaseStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Load deterministic handoff context for a stored Tapestry note or URL.")
    parser.add_argument("target", help="Note path or URL")
    parser.add_argument(
        "--project-root",
        default="",
        help="Optional project root containing the stored Tapestry artifacts",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd().resolve()
    store = KnowledgeBaseStore(target_root)
    target = args.target.strip()

    try:
        if target.startswith(("http://", "https://")):
            payload = store.load_handoff(url=target)
        else:
            payload = store.load_handoff(note_path=target)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
