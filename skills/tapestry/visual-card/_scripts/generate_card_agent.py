#!/usr/bin/env python3
"""
generate_card.py — Generate visual note cards from Tapestry knowledge base content

This script provides the template structure and basic extraction, then delegates
content synthesis to the Agent for intelligent content selection and presentation.

Usage:
    python generate_card.py --chapter "data/books/topic/chapter"
    python generate_card.py --chapter "ai-and-research/model-training" --output "data/cards"
    python generate_card.py --chapter "markets-and-trading/market-structure" --html-only
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


def find_project_root() -> Path:
    """Find the Tapestry project root by looking for data/ or knowledge-base/ directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "data").exists() or (current / "knowledge-base").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find Tapestry project root (no data/ or knowledge-base/ directory found)")


def parse_chapter_content(chapter_path: Path) -> Dict:
    """Parse a knowledge base chapter's markdown file."""
    # Try index.md first, then .md file with same name as directory
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
            # Parse YAML-like frontmatter
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"')
            content = parts[2]

    return {
        "frontmatter": frontmatter,
        "content": content.strip(),
        "raw": content
    }


def prepare_context_for_agent(chapter_data: Dict, chapter_name: str, topic_name: str) -> Dict:
    """
    Prepare a context package for the Agent to synthesize the card content.

    The Agent will receive:
    - The full chapter content
    - Template structure requirements
    - Design guidelines

    And will decide:
    - What framework to extract (2-6 components)
    - What insights to highlight (3-4 items)
    - What key points to emphasize (dark panel content)
    - How to structure the narrative
    """

    return {
        "source": {
            "content": chapter_data["content"],
            "chapter_name": chapter_name,
            "topic_name": topic_name,
            "frontmatter": chapter_data.get("frontmatter", {})
        },
        "template_requirements": {
            "framework": {
                "description": "Extract or synthesize a 2-6 component framework that captures the core structure",
                "format": "Each component needs: letter (first char), name (short), description (1-2 lines)",
                "example": {"letter": "M", "name": "模型", "description": "核心模型架构与设计原则"}
            },
            "insights": {
                "description": "Extract 3-4 key insights or takeaways (light panel)",
                "format": "Each insight needs: title (bold statement), description (1-2 lines)",
                "example": {"title": "数据质量优先", "description": "高质量的小数据集优于低质量的大数据集"}
            },
            "key_points": {
                "description": "Extract key points for narrative (dark panel)",
                "format": "Two blocks, each with: title + 4-5 bullet points",
                "block1": "First major theme or concept area",
                "block2": "Second major theme or application area"
            },
            "metadata": {
                "title": "Extract main title (bilingual if possible)",
                "thesis": "Write a 2-3 line provocative thesis statement",
                "conclusion": "Extract or write a memorable closing insight"
            }
        },
        "design_guidelines": {
            "language": "Match the source content language (Chinese/English)",
            "tone": "Professional but accessible, insight-driven",
            "framework_acronym": "Create a memorable acronym from framework letters",
            "emphasis": "Use <strong> tags for key terms in descriptions"
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Generate visual note cards from Tapestry KB content")
    parser.add_argument("--chapter", required=True, help="Chapter path (e.g., 'ai-and-research/model-training')")
    parser.add_argument("--output", default="data/cards", help="Output directory (default: data/cards)")
    parser.add_argument("--project-root", help="Tapestry project root (auto-detected if not provided)")
    parser.add_argument("--prepare-only", action="store_true", help="Only prepare context, don't generate card")
    parser.add_argument("--context-file", help="Load pre-synthesized context from JSON file")

    args = parser.parse_args()

    # Find project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = find_project_root()

    print(f"📁 Project root: {project_root}")

    # Resolve chapter path - try multiple locations
    chapter_path = None
    possible_paths = [
        project_root / "data" / "books" / args.chapter,
        project_root / "knowledge-base" / "books" / args.chapter,
        Path(args.chapter)
    ]

    for path in possible_paths:
        if path.exists():
            chapter_path = path
            break

    if not chapter_path:
        print(f"❌ Chapter not found: {args.chapter}")
        print(f"   Tried: {[str(p) for p in possible_paths]}")
        sys.exit(1)

    print(f"📖 Chapter: {chapter_path}")

    # Parse chapter content
    try:
        chapter_data = parse_chapter_content(chapter_path)
    except Exception as e:
        print(f"❌ Failed to parse chapter: {e}")
        sys.exit(1)

    # Extract names
    chapter_name = chapter_path.name if chapter_path.is_file() else chapter_path.stem
    if chapter_name.endswith('.md'):
        chapter_name = chapter_name[:-3]
    topic_name = chapter_path.parent.name

    # Prepare context for Agent
    context = prepare_context_for_agent(chapter_data, chapter_name, topic_name)

    if args.prepare_only:
        # Output context for Agent to process
        output_file = project_root / args.output / f"{chapter_name}_context.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ Context prepared: {output_file}")
        print(f"\n📋 Next step: Have the Agent synthesize this context into card content")
        print(f"   The Agent should analyze the content and decide:")
        print(f"   - What framework structure best represents the content")
        print(f"   - Which insights are most valuable")
        print(f"   - How to structure the narrative in the dark panel")
        sys.exit(0)

    # If we get here, we need Agent synthesis
    print(f"\n⚠️  This script now requires Agent synthesis.")
    print(f"   Run with --prepare-only to generate context, then have the Agent:")
    print(f"   1. Analyze the content")
    print(f"   2. Extract/synthesize framework, insights, and key points")
    print(f"   3. Generate the final HTML using the template")
    print(f"\n   Or use the legacy generate_card_legacy.py for automatic extraction")


if __name__ == "__main__":
    main()
