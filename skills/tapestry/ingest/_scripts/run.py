#!/usr/bin/env python3
"""Deterministic ingest runner for the Tapestry skill pack."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Project root is 4 levels up: ingest/_scripts/run.py -> ingest/ -> tapestry/ -> skills/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]
TAPESTRY_ROOT = Path(__file__).resolve().parents[2]

if str(TAPESTRY_ROOT) not in sys.path:
    sys.path.insert(0, str(TAPESTRY_ROOT))

from _src.crawlers.run import build_parser as build_crawler_parser
from _src.crawlers.run import run_cli


def build_parser() -> argparse.ArgumentParser:
    parser = build_crawler_parser()
    # Set default project root to the Tapestry project root (4 levels up)
    parser.set_defaults(project_root=str(PROJECT_ROOT))
    return parser


async def _run(args: argparse.Namespace) -> int:
    if not sys.stdin.isatty() and not args.text:
        args.text = sys.stdin.read().strip()
    return await run_cli(args)


if __name__ == "__main__":
    import asyncio

    raise SystemExit(asyncio.run(_run(build_parser().parse_args())))
