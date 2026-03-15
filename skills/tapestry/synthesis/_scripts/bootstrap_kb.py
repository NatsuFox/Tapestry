#!/usr/bin/env python3
"""Bootstrap the knowledge-base hierarchy for Tapestry synthesis."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create missing knowledge-base index.md scaffolding from the synthesis blueprint."
    )
    parser.add_argument(
        "--project-root",
        default="",
        help="Project root where knowledge-base should be created. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing index.md files instead of only creating missing ones.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd().resolve()
    blueprint_root = Path(__file__).resolve().parent.parent / "_kb_blueprint" / "knowledge-base"
    destination_root = project_root / "knowledge-base"
    destination_root.mkdir(parents=True, exist_ok=True)

    for source in blueprint_root.rglob("*"):
        relative = source.relative_to(blueprint_root)
        target = destination_root / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists() and not args.force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    print(destination_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
