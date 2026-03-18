#!/usr/bin/env python3
"""
generate_card.py — Generate visual note cards from Tapestry knowledge base content

Usage:
    python generate_card.py --chapter "data/books/topic/chapter"
    python generate_card.py --chapter "ai-and-research/model-training" --output "outputs/cards"
    python generate_card.py --chapter "markets-and-trading/market-structure" --html-only
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


def extract_key_points_from_content(content: str) -> Dict:
    """
    Extract key points and sections from the content for the dark panel.
    Returns a dict with block titles and items.
    """
    # Try to find sections with headers
    sections = []
    current_section = None

    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Look for ## or ### headers
        if re.match(r'^##\s+(.+)$', line):
            header = re.match(r'^##\s+(.+)$', line).group(1)
            if current_section:
                sections.append(current_section)
            current_section = {'title': header, 'items': []}
        elif current_section and line.strip().startswith(('- ', '* ', '1. ', '2. ', '3. ')):
            # Extract bullet point or numbered item
            item = re.sub(r'^[-*\d]+\.\s*', '', line.strip())
            # Remove markdown formatting
            item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
            item = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', item)
            if item and len(item) > 10:  # Skip very short items
                current_section['items'].append(item[:100])  # Limit length

    if current_section:
        sections.append(current_section)

    # Select best sections for the two blocks
    result = {
        'block1_title': '关键概念',
        'block1_items': ['核心定义与边界', '理论基础与背景', '发展历程与演进', '当前研究前沿'],
        'block2_title': '实践应用',
        'block2_items': ['典型应用场景', '实施方法与步骤', '常见问题与解决', '最佳实践建议', '未来发展方向'],
        'conclusion': '深入理解这些概念,能够帮助我们',
        'conclusion_highlight': '构建系统化的知识体系'
    }

    if len(sections) >= 2:
        # Use first section for block1
        result['block1_title'] = sections[0]['title'][:20]
        if sections[0]['items']:
            result['block1_items'] = sections[0]['items'][:4]

        # Use second section for block2
        result['block2_title'] = sections[1]['title'][:20]
        if sections[1]['items']:
            result['block2_items'] = sections[1]['items'][:5]
    elif len(sections) == 1:
        # Use the one section we have
        result['block1_title'] = sections[0]['title'][:20]
        if sections[0]['items']:
            result['block1_items'] = sections[0]['items'][:4]

    # Try to extract a conclusion from the last paragraph
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
    if paragraphs:
        last_para = paragraphs[-1]
        # Look for sentences with key phrases
        if any(word in last_para for word in ['总结', '结论', '综上', '因此', 'conclusion', 'summary']):
            sentences = re.split(r'[。.!！]', last_para)
            if sentences:
                result['conclusion'] = sentences[0][:50]
                if len(sentences) > 1:
                    result['conclusion_highlight'] = sentences[1][:30]

    return result


def extract_framework_from_content(content: str) -> Optional[List[Dict]]:
    """
    Try to extract a framework structure from the content.
    Looks for numbered lists, bullet points, or section headers.
    """
    # Look for numbered sections (1. 2. 3.)
    numbered_pattern = r'^\d+\.\s+\*\*(.+?)\*\*[:\s]*(.+?)(?=\n\d+\.|\n#|\Z)'
    matches = re.findall(numbered_pattern, content, re.MULTILINE | re.DOTALL)

    if matches and len(matches) >= 2:
        framework = []
        for title, desc in matches[:6]:  # Max 6 components
            # Extract first letter for badge
            letter = title.strip()[0].upper()
            framework.append({
                "letter": letter,
                "name": title.strip()[:20],  # Limit length
                "description": desc.strip()[:100]  # Limit length
            })
        return framework

    # Look for bullet points with bold headers
    bullet_pattern = r'[-*]\s+\*\*(.+?)\*\*[:\s]*(.+?)(?=\n[-*]|\n#|\Z)'
    matches = re.findall(bullet_pattern, content, re.MULTILINE | re.DOTALL)

    if matches and len(matches) >= 2:
        framework = []
        for title, desc in matches[:6]:
            letter = title.strip()[0].upper()
            framework.append({
                "letter": letter,
                "name": title.strip()[:20],
                "description": desc.strip()[:100]
            })
        return framework

    return None


def generate_html_card(
    chapter_data: Dict,
    chapter_name: str,
    topic_name: str,
    template_path: Path,
    output_path: Path,
    primary_color: str = "#1a7a6d",
    accent_color: str = "#e8713a"
) -> Path:
    """Generate the HTML card file from the template."""

    # Load template
    template = template_path.read_text(encoding="utf-8")

    content = chapter_data["content"]

    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else chapter_name

    # Extract key points for dark panel
    key_points = extract_key_points_from_content(content)

    # Try to extract framework
    framework = extract_framework_from_content(content)
    if not framework:
        # Create a default 4-component framework
        framework = [
            {"letter": "C", "name": "概念", "description": "核心概念与定义"},
            {"letter": "M", "name": "方法", "description": "实践方法与技巧"},
            {"letter": "I", "name": "洞察", "description": "关键洞察与发现"},
            {"letter": "A", "name": "应用", "description": "实际应用场景"}
        ]

    # Determine column count
    col_count = len(framework)
    grid_style = f'style="grid-template-columns: repeat({col_count}, 1fr)"' if col_count != 4 else ""

    # Build framework HTML
    fw_html = ""
    for i, fw in enumerate(framework):
        fw_html += f'''    <div class="fw-card">
      <div class="badge">
        <div class="letter">{fw["letter"]}</div>
        <div class="name">{fw["name"]}</div>
      </div>
      <div class="desc">{fw["description"]}</div>
    </div>
'''

    # Extract insights (numbered lists or key points)
    insights = []
    insight_pattern = r'^\d+\.\s+\*\*(.+?)\*\*[:\s]*(.+?)(?=\n\d+\.|\n#|\Z)'
    insight_matches = re.findall(insight_pattern, content, re.MULTILINE | re.DOTALL)

    if insight_matches:
        for title, desc in insight_matches[:4]:
            insights.append({
                "title": title.strip(),
                "description": desc.strip()[:150]
            })
    else:
        # Fallback: extract from bullet points
        bullet_pattern = r'[-*]\s+\*\*(.+?)\*\*[:\s]*(.+?)(?=\n[-*]|\n#|\Z)'
        bullet_matches = re.findall(bullet_pattern, content, re.MULTILINE | re.DOTALL)
        for title, desc in bullet_matches[:4]:
            insights.append({
                "title": title.strip(),
                "description": desc.strip()[:150]
            })

    # Ensure we have at least 3 insights
    while len(insights) < 3:
        insights.append({
            "title": f"关键点 {len(insights) + 1}",
            "description": "待补充的洞察内容"
        })

    # Build insights HTML
    insights_html = ""
    for i, insight in enumerate(insights[:4], 1):
        insights_html += f'''      <div class="insight-item">
        <div class="insight-num">{i}</div>
        <div class="insight-content">
          <h4>{insight["title"]}</h4>
          <p>{insight["description"]}</p>
        </div>
      </div>
'''

    # Create framework acronym
    acronym = "".join([fw["letter"] for fw in framework])

    # Generate replacements
    replacements = {
        "{{CARD_TITLE}}": title,
        "{{TOPIC_LABEL_EN}}": topic_name.upper().replace("-", " "),
        "{{SUBTOPIC_LABEL_EN}}": "KNOWLEDGE BASE",
        "{{SOURCE_LABEL}}": "TAPESTRY",
        "{{TITLE_EN}}": title if re.search(r'[a-zA-Z]', title) else "Knowledge Card",
        "{{TITLE_CN}}": title if not re.search(r'[a-zA-Z]', title) else "知识卡片",
        "{{THESIS_LINE_1}}": f"来自 Tapestry 知识库的",
        "{{THESIS_LINE_2}}": "结构化知识总结,",
        "{{THESIS_KEYWORD}}": "系统化理解",
        "{{THESIS_LINE_3}}": "核心概念",
        "{{DARK_ICON}}": "⚡",
        "{{DARK_SECTION_TITLE}}": "核心要点",
        "{{BLOCK1_TITLE}}": key_points['block1_title'],
        "{{BLOCK1_ITEM1}}": key_points['block1_items'][0] if len(key_points['block1_items']) > 0 else "核心定义与边界",
        "{{BLOCK1_ITEM2}}": key_points['block1_items'][1] if len(key_points['block1_items']) > 1 else "理论基础与背景",
        "{{BLOCK1_ITEM3}}": key_points['block1_items'][2] if len(key_points['block1_items']) > 2 else "发展历程与演进",
        "{{BLOCK1_ITEM4}}": key_points['block1_items'][3] if len(key_points['block1_items']) > 3 else "当前研究前沿",
        "{{BLOCK2_TITLE}}": key_points['block2_title'],
        "{{BLOCK2_ITEM1}}": key_points['block2_items'][0] if len(key_points['block2_items']) > 0 else "典型应用场景",
        "{{BLOCK2_ITEM2}}": key_points['block2_items'][1] if len(key_points['block2_items']) > 1 else "实施方法与步骤",
        "{{BLOCK2_ITEM3}}": key_points['block2_items'][2] if len(key_points['block2_items']) > 2 else "常见问题与解决",
        "{{BLOCK2_ITEM4}}": key_points['block2_items'][3] if len(key_points['block2_items']) > 3 else "最佳实践建议",
        "{{BLOCK2_ITEM5}}": key_points['block2_items'][4] if len(key_points['block2_items']) > 4 else "未来发展方向",
        "{{CONCLUSION_LABEL}}": "核心洞察",
        "{{CONCLUSION_TEXT}}": key_points['conclusion'],
        "{{CONCLUSION_HIGHLIGHT}}": key_points['conclusion_highlight'],
        "{{LIGHT_SECTION_TITLE}}": "关键洞察",
        "{{FORMULA}}": f"{acronym} Framework",
        "{{FORMULA_SUBTEXT}}": f"{' × '.join([fw['letter'] for fw in framework])} = 完整理解",
        "{{CLOSING_THOUGHT}}": "系统化的知识组织是深度理解的基础",
        "{{FOOTER_LEFT}}": "tapestry.knowledge-base",
        "{{FOOTER_BRAND}}": "TAPESTRY",
        "{{FOOTER_FRAMEWORK}}": f"{acronym} FRAMEWORK",
        "{{FOOTER_YEAR}}": str(datetime.now().year)
    }

    # Replace framework row - find the section and replace it entirely
    fw_start = template.find('<div class="framework-row">')
    fw_end = template.find('<!-- ====== SECTION 4', fw_start)

    if fw_start != -1 and fw_end != -1:
        # Find the closing </div> before the comment
        closing_div = template.rfind('</div>', fw_start, fw_end)
        if closing_div != -1:
            fw_end = closing_div + 6  # len('</div>')

        fw_replacement = f'<div class="framework-row" {grid_style}>\n{fw_html}  </div>\n\n  '
        template = template[:fw_start] + fw_replacement + template[fw_end:]

    # Replace insights section
    insights_start = template.find('<div class="panel-light">')
    insights_title_end = template.find('</div>', template.find('<div class="section-title">', insights_start))
    insights_end = template.find('<!-- ====== SECTION 5', insights_start)

    if insights_start != -1 and insights_title_end != -1 and insights_end != -1:
        # Find content between title and section end
        content_start = insights_title_end + 6  # len('</div>')
        # Find the closing </div> before the comment
        closing_div = template.rfind('</div>', insights_start, insights_end)
        if closing_div != -1:
            insights_end = closing_div

        insights_replacement = f'\n{insights_html}    '
        template = template[:content_start] + insights_replacement + template[insights_end:]

    # Apply all replacements
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    # Customize colors if provided
    if primary_color != "#1a7a6d":
        template = template.replace("--primary: #1a7a6d", f"--primary: {primary_color}")
    if accent_color != "#e8713a":
        template = template.replace("--accent: #e8713a", f"--accent: {accent_color}")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template, encoding="utf-8")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate visual note cards from Tapestry KB content")
    parser.add_argument("--chapter", required=True, help="Chapter path (e.g., 'ai-and-research/model-training')")
    parser.add_argument("--output", default="data/cards", help="Output directory (default: data/cards)")
    parser.add_argument("--project-root", help="Tapestry project root (auto-detected if not provided)")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only, skip PNG")
    parser.add_argument("--scale", type=float, default=1.5, help="PNG scale factor (default: 1.5)")
    parser.add_argument("--primary-color", default="#1a7a6d", help="Primary color (default: teal)")
    parser.add_argument("--accent-color", default="#e8713a", help="Accent color (default: orange)")

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
    chapter_name = chapter_path.name
    topic_name = chapter_path.parent.name

    # Setup output
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = project_root / args.output / f"{timestamp}-{chapter_name}"
    output_html = output_dir / f"{chapter_name}.html"

    # Find template
    template_path = project_root / "skills" / "tapestry" / "visual-card" / "_templates" / "card_template.html"
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    # Generate HTML
    print(f"🎨 Generating HTML card...")
    try:
        html_path = generate_html_card(
            chapter_data,
            chapter_name,
            topic_name,
            template_path,
            output_html,
            args.primary_color,
            args.accent_color
        )
        print(f"✅ HTML generated: {html_path}")
    except Exception as e:
        print(f"❌ Failed to generate HTML: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Generate PNG if requested
    if not args.html_only:
        output_png = output_dir / f"{chapter_name}.png"
        html2png_script = project_root / "skills" / "tapestry" / "visual-card" / "_scripts" / "html2png.py"

        if html2png_script.exists():
            print(f"🖼️  Generating PNG (scale={args.scale})...")
            import subprocess
            try:
                result = subprocess.run(
                    [sys.executable, str(html2png_script), str(html_path), str(output_png), f"--scale={args.scale}"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(result.stdout)
                print(f"✅ PNG generated: {output_png}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  PNG generation failed: {e}")
                print(f"   You can generate it manually: python {html2png_script} {html_path} {output_png}")
        else:
            print(f"⚠️  html2png.py not found, skipping PNG generation")

    print(f"\n📦 Output directory: {output_dir}")
    print(f"   HTML: {output_html.name}")
    if not args.html_only:
        print(f"   PNG:  {output_png.name}")


if __name__ == "__main__":
    main()
