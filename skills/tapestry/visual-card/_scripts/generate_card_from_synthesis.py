#!/usr/bin/env python3
"""
generate_card_from_synthesis.py — Generate visual cards from Agent-synthesized content

This script takes a synthesis JSON file (created by Agent analysis) and generates
the final HTML/PNG visual card.

Usage:
    python generate_card_from_synthesis.py --synthesis synthesis.json
    python generate_card_from_synthesis.py --synthesis synthesis.json --html-only
    python generate_card_from_synthesis.py --synthesis synthesis.json --scale 2.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def find_project_root() -> Path:
    """Find the Tapestry project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "data").exists() or (current / "knowledge-base").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find Tapestry project root")


def load_synthesis(synthesis_path: Path) -> dict:
    """Load the Agent-synthesized content."""
    if not synthesis_path.exists():
        raise FileNotFoundError(f"Synthesis file not found: {synthesis_path}")

    return json.loads(synthesis_path.read_text(encoding="utf-8"))


def generate_html_from_synthesis(
    synthesis: dict,
    template_path: Path,
    output_path: Path,
    primary_color: str = "#1a7a6d",
    accent_color: str = "#e8713a"
) -> Path:
    """Generate HTML card from synthesized content."""

    # Load template
    template = template_path.read_text(encoding="utf-8")

    # Extract synthesis data
    meta = synthesis["metadata"]
    framework = synthesis["framework"]
    insights = synthesis["insights"]
    dark = synthesis["dark_panel"]

    # Build framework HTML
    col_count = len(framework["components"])
    grid_style = f'style="grid-template-columns: repeat({col_count}, 1fr)"' if col_count != 4 else ""

    fw_html = ""
    for comp in framework["components"]:
        fw_html += f'''    <div class="fw-card">
      <div class="badge">
        <div class="letter">{comp["letter"]}</div>
        <div class="name">{comp["name"]}</div>
      </div>
      <div class="desc">{comp["description"]}</div>
    </div>
'''

    # Build insights HTML
    insights_html = ""
    for insight in insights:
        insights_html += f'''      <div class="insight-item">
        <div class="insight-num">{insight["number"]}</div>
        <div class="insight-content">
          <h4>{insight["title"]}</h4>
          <p>{insight["description"]}</p>
        </div>
      </div>
'''

    # Build dark panel HTML
    block1_items = "\n        ".join([f"<li>{item}</li>" for item in dark["block1"]["items"]])
    block2_items = "\n        ".join([f"<li>{item}</li>" for item in dark["block2"]["items"]])

    # Create replacements
    replacements = {
        "{{CARD_TITLE}}": meta["title_en"],
        "{{TOPIC_LABEL_EN}}": meta["topic_label"],
        "{{SUBTOPIC_LABEL_EN}}": "KNOWLEDGE BASE",
        "{{SOURCE_LABEL}}": meta["source_label"],
        "{{TITLE_EN}}": meta["title_en"],
        "{{TITLE_CN}}": meta["title_cn"],
        "{{THESIS_LINE_1}}": meta["thesis"].split("<strong>")[0],
        "{{THESIS_LINE_2}}": "",
        "{{THESIS_KEYWORD}}": meta["thesis"].split("<strong>")[1].split("</strong>")[0] if "<strong>" in meta["thesis"] else "",
        "{{THESIS_LINE_3}}": meta["thesis"].split("</strong>")[1] if "</strong>" in meta["thesis"] else "",
        "{{DARK_ICON}}": dark["icon"],
        "{{DARK_SECTION_TITLE}}": dark["section_title"],
        "{{BLOCK1_TITLE}}": dark["block1"]["title"],
        "{{BLOCK2_TITLE}}": dark["block2"]["title"],
        "{{CONCLUSION_LABEL}}": dark["conclusion"]["label"],
        "{{CONCLUSION_TEXT}}": dark["conclusion"]["text"],
        "{{CONCLUSION_HIGHLIGHT}}": dark["conclusion"]["highlight"],
        "{{LIGHT_SECTION_TITLE}}": "关键洞察",
        "{{FORMULA}}": framework["formula"],
        "{{FORMULA_SUBTEXT}}": framework["formula_subtext"],
        "{{CLOSING_THOUGHT}}": synthesis["closing_thought"],
        "{{FOOTER_LEFT}}": "tapestry.knowledge-base",
        "{{FOOTER_BRAND}}": "TAPESTRY",
        "{{FOOTER_FRAMEWORK}}": f"{framework['acronym']} FRAMEWORK",
        "{{FOOTER_YEAR}}": str(datetime.now().year)
    }

    # Replace framework row
    fw_start = template.find('<div class="framework-row">')
    fw_end = template.find('<!-- ====== SECTION 4', fw_start)

    if fw_start != -1 and fw_end != -1:
        closing_div = template.rfind('</div>', fw_start, fw_end)
        if closing_div != -1:
            fw_end = closing_div + 6

        fw_replacement = f'<div class="framework-row" {grid_style}>\n{fw_html}  </div>\n\n  '
        template = template[:fw_start] + fw_replacement + template[fw_end:]

    # Replace insights section
    insights_start = template.find('<div class="panel-light">')
    insights_title_end = template.find('</div>', template.find('<div class="section-title">', insights_start))
    insights_end = template.find('<!-- ====== SECTION 5', insights_start)

    if insights_start != -1 and insights_title_end != -1 and insights_end != -1:
        content_start = insights_title_end + 6
        closing_div = template.rfind('</div>', insights_start, insights_end)
        if closing_div != -1:
            insights_end = closing_div

        insights_replacement = f'\n{insights_html}    '
        template = template[:content_start] + insights_replacement + template[insights_end:]

    # Replace dark panel content
    # Find and replace block1 items
    block1_start = template.find('<div class="block-title">{{BLOCK1_TITLE}}</div>')
    if block1_start != -1:
        ul_start = template.find('<ul>', block1_start)
        ul_end = template.find('</ul>', ul_start)
        if ul_start != -1 and ul_end != -1:
            template = template[:ul_start + 4] + f"\n        {block1_items}\n      " + template[ul_end:]

    # Find and replace block2 items
    block2_start = template.find('<div class="block-title">{{BLOCK2_TITLE}}</div>')
    if block2_start != -1:
        ul_start = template.find('<ul>', block2_start)
        ul_end = template.find('</ul>', ul_start)
        if ul_start != -1 and ul_end != -1:
            template = template[:ul_start + 4] + f"\n        {block2_items}\n      " + template[ul_end:]

    # Apply all replacements
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    # Customize colors
    if primary_color != "#1a7a6d":
        template = template.replace("--primary: #1a7a6d", f"--primary: {primary_color}")
    if accent_color != "#e8713a":
        template = template.replace("--accent: #e8713a", f"--accent: {accent_color}")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template, encoding="utf-8")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate visual cards from Agent synthesis")
    parser.add_argument("--synthesis", required=True, help="Path to synthesis JSON file")
    parser.add_argument("--output", help="Output directory (default: same as synthesis)")
    parser.add_argument("--project-root", help="Tapestry project root (auto-detected)")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only, skip PNG")
    parser.add_argument("--scale", type=float, default=1.5, help="PNG scale factor (default: 1.5)")
    parser.add_argument("--primary-color", default="#1a7a6d", help="Primary color")
    parser.add_argument("--accent-color", default="#e8713a", help="Accent color")

    args = parser.parse_args()

    # Find project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = find_project_root()

    print(f"📁 Project root: {project_root}")

    # Load synthesis
    synthesis_path = Path(args.synthesis)
    if not synthesis_path.is_absolute():
        synthesis_path = project_root / synthesis_path

    print(f"📋 Loading synthesis: {synthesis_path}")

    try:
        synthesis = load_synthesis(synthesis_path)
    except Exception as e:
        print(f"❌ Failed to load synthesis: {e}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_dir = project_root / args.output
    else:
        output_dir = synthesis_path.parent

    # Generate output filename from synthesis metadata
    chapter_name = synthesis["metadata"]["title_en"].lower().replace(" ", "-")
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_subdir = output_dir / f"{timestamp}-{chapter_name}"
    output_html = output_subdir / f"{chapter_name}.html"

    # Find template
    template_path = project_root / "skills" / "tapestry" / "visual-card" / "_templates" / "card_template.html"
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    # Generate HTML
    print(f"🎨 Generating HTML card...")
    try:
        html_path = generate_html_from_synthesis(
            synthesis,
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
        output_png = output_subdir / f"{chapter_name}.png"
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

    print(f"\n📦 Output directory: {output_subdir}")
    print(f"   HTML: {output_html.name}")
    if not args.html_only:
        print(f"   PNG:  {output_png.name}")


if __name__ == "__main__":
    main()
