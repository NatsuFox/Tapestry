#!/usr/bin/env python3
"""Deterministic ingest runner for the Tapestry skill pack."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from _src.crawlers.run import build_parser as build_crawler_parser
from _src.crawlers.run import run_cli


def build_parser() -> argparse.ArgumentParser:
    return build_crawler_parser()


async def _run(args: argparse.Namespace) -> int:
    if not sys.stdin.isatty() and not args.text:
        args.text = sys.stdin.read().strip()
    return await run_cli(args)


if __name__ == "__main__":
    import asyncio

    raise SystemExit(asyncio.run(_run(build_parser().parse_args())))
