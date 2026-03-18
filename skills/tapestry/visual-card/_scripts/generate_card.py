#!/usr/bin/env python3
"""
generate_card.py — Agent-driven visual card generation

This script orchestrates the Agent-driven workflow:
1. Prepare context (source content + template specification)
2. Invoke Agent to synthesize content mapping
3. Generate HTML/PNG from Agent's synthesis

Usage:
    python generate_card.py --chapter "ai-and-development-tools/ai-agent-architecture.md"
    python generate_card.py --chapter "ai-and-development-tools/agent-skills.md" --html-only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def find_project_root() -> Path:
    """Find the Tapestry project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "data").exists() or (current / "skills").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find Tapestry project root")


def main():
    parser = argparse.ArgumentParser(description="Generate visual cards using Agent-driven synthesis")
    parser.add_argument("--chapter", required=True, help="Chapter path (e.g., 'ai-and-development-tools/ai-agent-architecture.md')")
    parser.add_argument("--output", help="Output directory (default: data/cards)")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only, skip PNG")
    parser.add_argument("--scale", type=float, default=1.5, help="PNG scale factor (default: 1.5)")
    parser.add_argument("--use-legacy", action="store_true", help="Use legacy hardcoded extraction instead of Agent")

    args = parser.parse_args()

    project_root = find_project_root()
    scripts_dir = project_root / "skills" / "tapestry" / "visual-card" / "_scripts"

    # If legacy mode requested, use it directly
    if args.use_legacy:
        print("⚠️  Using legacy hardcoded extraction mode")
        legacy_script = scripts_dir / "generate_card_legacy.py"
        cmd = [sys.executable, str(legacy_script), "--chapter", args.chapter]
        if args.output:
            cmd.extend(["--output", args.output])
        if args.html_only:
            cmd.append("--html-only")
        result = subprocess.run(cmd, cwd=project_root)
        sys.exit(result.returncode)

    print(f"📁 Project root: {project_root}")
    print(f"📖 Chapter: {args.chapter}")

    # Step 1: Prepare context for Agent
    print(f"\n🔍 Step 1: Preparing context...")
    prepare_script = scripts_dir / "prepare_card_context.py"

    try:
        result = subprocess.run(
            [sys.executable, str(prepare_script), "--chapter", args.chapter],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )
        context = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to prepare context: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse context JSON: {e}")
        sys.exit(1)

    print(f"✅ Context prepared")
    print(f"   Source: {len(context['source']['content'])} characters")
    print(f"   Template spec: {len(context['template_specification'])} characters")

    # Step 2: Invoke Agent to synthesize content
    print(f"\n🤖 Step 2: Invoking Agent for content synthesis...")
    print(f"\n{'='*60}")
    print("AGENT TASK:")
    print("="*60)
    print(context['instructions'])
    print(f"\nSOURCE CONTENT:")
    print("-"*60)
    print(context['source']['content'][:500] + "..." if len(context['source']['content']) > 500 else context['source']['content'])
    print(f"\nTEMPLATE SPECIFICATION:")
    print("-"*60)
    print(context['template_specification'][:500] + "..." if len(context['template_specification']) > 500 else context['template_specification'])
    print("="*60)
    print("\n⚠️  Agent synthesis not yet implemented!")
    print("    Please implement Agent invocation to read the context and generate synthesis JSON")
    print("    Expected output: JSON with metadata, framework, insights, dark_panel, closing_thought")
    print("\n💡 For now, falling back to legacy hardcoded extraction...")

    # Fallback to legacy script
    legacy_script = scripts_dir / "generate_card_legacy.py"
    cmd = [sys.executable, str(legacy_script), "--chapter", args.chapter]
    if args.output:
        cmd.extend(["--output", args.output])
    if args.html_only:
        cmd.append("--html-only")

    result = subprocess.run(cmd, cwd=project_root)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
