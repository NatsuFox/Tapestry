#!/usr/bin/env python3
"""
prepare_card_context.py — Prepare context for Agent-driven card generation

This script extracts the source content and provides the template specification.
The Agent reads both and autonomously decides how to map content to template blocks.

Usage:
    python prepare_card_context.py --chapter "ai-and-research/model-training"
"""

import argparse
import json
import sys
from pathlib import Path

TAPESTRY_ROOT = Path(__file__).resolve().parents[2]
if str(TAPESTRY_ROOT) not in sys.path:
    sys.path.insert(0, str(TAPESTRY_ROOT))

from _src.config import TapestryConfig, skill_root


def find_project_root() -> Path:
    """Find the Tapestry project root."""
    return TapestryConfig.load().resolve_project_root()


def parse_chapter_content(chapter_path: Path) -> dict:
    """Parse a knowledge base chapter's markdown file."""
    possible_files = [
        chapter_path / "index.md",
        chapter_path.with_suffix(".md") if chapter_path.is_dir() else chapter_path,
        chapter_path
    ]

    content_file = None
    for f in possible_files:
        if f.exists() and f.is_file():
            content_file = f
            break

    if not content_file:
        raise FileNotFoundError(f"No markdown file found in: {chapter_path}")

    content = content_file.read_text(encoding="utf-8")

    # Extract frontmatter if present
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"')
            content = parts[2]

    return {
        "frontmatter": frontmatter,
        "content": content.strip()
    }


def main():
    parser = argparse.ArgumentParser(description="Prepare context for Agent-driven card generation")
    parser.add_argument("--chapter", required=True, help="Chapter path")
    parser.add_argument("--project-root", help="Project root (auto-detected)")

    args = parser.parse_args()

    # Find project root
    config = TapestryConfig.load()
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else find_project_root()
    data_root = config.resolve_data_root(project_root)

    # Resolve chapter path
    chapter_path = None
    for path in [
        data_root / "books" / args.chapter,
        project_root / "knowledge-base" / "books" / args.chapter,
        Path(args.chapter)
    ]:
        if path.exists():
            chapter_path = path
            break

    if not chapter_path:
        print(f"❌ Chapter not found: {args.chapter}")
        sys.exit(1)

    # Parse content
    try:
        chapter_data = parse_chapter_content(chapter_path)
    except Exception as e:
        print(f"❌ Failed to parse: {e}")
        sys.exit(1)

    # Extract names
    chapter_name = chapter_path.name if chapter_path.is_file() else chapter_path.stem
    if chapter_name.endswith('.md'):
        chapter_name = chapter_name[:-3]
    topic_name = chapter_path.parent.name

    # Load template specification
    template_spec_path = skill_root() / "visual-card" / "_templates" / "card_template_spec.md"
    if not template_spec_path.exists():
        print(f"❌ Template specification not found: {template_spec_path}")
        sys.exit(1)
    template_spec = template_spec_path.read_text(encoding="utf-8")

    # Prepare context
    context = {
        "source": {
            "content": chapter_data["content"],
            "frontmatter": chapter_data["frontmatter"],
            "chapter_name": chapter_name,
            "topic_name": topic_name
        },
        "template_specification": template_spec,
        "instructions": """
You are generating a visual note card. Please read the template specification carefully
and analyze the source content to decide how to fill each of the 7 template blocks.

Your task:
1. Read the full source content
2. Follow the template specification to understand each block's purpose
3. Make intelligent decisions about what content fits each block
4. Output a JSON synthesis with all blocks filled

The template specification describes:
- What each block is for
- How to extract or synthesize content for it
- Quality criteria for good vs bad decisions
- Examples of good content mapping

Be autonomous: make decisions based on content analysis, not rigid rules.
Prioritize quality and narrative flow over mechanical extraction.
"""
    }

    # Output context
    print(json.dumps(context, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
