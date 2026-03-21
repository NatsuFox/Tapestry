#!/usr/bin/env python3
"""
generate_card.py — Prepare context for Agent-driven visual card generation

This script prepares and prints the full context needed for Agent synthesis.
The Agent (Claude) reads this output, synthesizes content mapping per the
template specification, writes a synthesis JSON, then calls
generate_card_from_synthesis.py to produce the final HTML/PNG.

Usage (called by Agent via SKILL):
    python generate_card.py --chapter "ai-and-development-tools/ai-agent-architecture.md"

Legacy fallback (skip Agent synthesis):
    python generate_card.py --chapter "..." --use-legacy
"""

import argparse
import subprocess
import sys
from pathlib import Path

TAPESTRY_ROOT = Path(__file__).resolve().parents[2]
if str(TAPESTRY_ROOT) not in sys.path:
    sys.path.insert(0, str(TAPESTRY_ROOT))

from _src.config import TapestryConfig, skill_root


def find_project_root() -> Path:
    return TapestryConfig.load().resolve_project_root()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--output", help="Output directory (default: _data/cards)")
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--scale", type=float, default=1.5)
    parser.add_argument("--use-legacy", action="store_true", help="Skip Agent synthesis, use legacy extraction")
    args = parser.parse_args()

    project_root = find_project_root()
    scripts_dir = skill_root() / "visual-card" / "_scripts"

    if args.use_legacy:
        cmd = [sys.executable, str(scripts_dir / "generate_card_legacy.py"), "--chapter", args.chapter]
        if args.output:
            cmd.extend(["--output", args.output])
        if args.html_only:
            cmd.append("--html-only")
        sys.exit(subprocess.run(cmd, cwd=project_root).returncode)

    # Prepare and print context for Agent
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "prepare_card_context.py"), "--chapter", args.chapter],
        capture_output=True, text=True, cwd=project_root
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    # Output the context JSON for the Agent to read
    print(result.stdout)


if __name__ == "__main__":
    main()
