#!/usr/bin/env python3
"""Bootstrap the knowledge-base hierarchy for Tapestry synthesis."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create missing knowledge-base index.md scaffolding from a template."
    )
    parser.add_argument(
        "--project-root",
        default="",
        help="Project root where knowledge-base should be created. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--template",
        default=None,
        choices=["default", "comprehensive"],
        help="Template to use: 'default' (minimal, agent-adaptable) or 'comprehensive' (predefined topics). If not specified, uses config setting.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing index.md files instead of only creating missing ones.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    # Determine template: CLI flag > config > default
    template = args.template
    config = None
    if not template:
        # Try to load from config
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
            from _src.config import TapestryConfig
            config = TapestryConfig.load()
            template = config.synthesis.kb_template
        except Exception:
            template = "default"

    if config is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
            from _src.config import TapestryConfig
            config = TapestryConfig.load()
        except Exception:
            config = None

    project_root = (
        Path(args.project_root).expanduser().resolve()
        if args.project_root
        else (config.resolve_project_root() if config else Path.cwd().resolve())
    )

    template_root = Path(__file__).resolve().parent.parent / "_kb_templates" / template
    destination_root = config.resolve_data_root(project_root) / "books" if config else project_root / "_data" / "books"

    if not template_root.exists():
        print(f"Error: Template '{template}' not found at {template_root}", file=sys.stderr)
        return 1

    destination_root.mkdir(parents=True, exist_ok=True)

    for source in template_root.rglob("*"):
        relative = source.relative_to(template_root)
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
