---
name: visual-card
description: Generate professional visual note cards (视觉笔记卡片/信息图) from knowledge base content as single-page HTML infographics with PNG export. Use when users want to create visual summaries, knowledge cards, infographics, or poster-style visualizations of topics from the knowledge base.
argument-hint: [topic-or-chapter-path]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Visual Card

Generate professional visual note cards from knowledge base content: **$ARGUMENTS**

## When to use this skill

Use this skill when:
- A user wants to create a visual note card or infographic from KB content
- The user asks to "visualize", "create a card", "make an infographic", or "generate a visual summary"
- The user mentions 视觉笔记, 知识卡片, 信息图, or one-pager summary
- You need to present knowledge base content in a shareable, poster-style format
- The user wants to export KB content for social media or presentations

## Purpose

This skill transforms structured knowledge base content into beautiful, information-dense visual cards following an editorial magazine aesthetic. It produces:

1. A self-contained HTML file with embedded styles and export functionality
2. A high-quality PNG image (via Playwright rendering)

The cards follow a fixed layout structure optimized for readability and social sharing.

## Workflow

### Step 1: Identify the Source Content

Resolve the target from the argument:
- If a specific chapter path is provided (e.g., "ai-and-research/model-training"), use that chapter
- If a topic is provided (e.g., "markets-and-trading"), offer to generate cards for its chapters
- If no argument, list available topics and ask the user to choose

```bash
# List available topics
ls -d data/books/*/
```

### Step 2: Load the Content

Read the target chapter's `index.md` file to extract:
- Chapter title and description
- Main content sections
- Key concepts and frameworks
- Insights and takeaways

```bash
# Example: Read a chapter
cat data/books/ai-and-research/model-training-and-optimization/index.md
```

### Step 3: Generate the Visual Card

Run the card generator script with the chapter path:

```bash
cd /root/Workspace/PROJECTS/powers/Tapestry
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "data/books/ai-and-research/model-training-and-optimization" \
  --output "data/cards"
```

The script will:
1. Parse the chapter content
2. Extract or synthesize a framework structure
3. Generate the HTML card using the template
4. Render the PNG using Playwright
5. Save both files to the output directory

### Step 4: Present the Results

Report back with:
- The generated PNG path (primary deliverable)
- The HTML path (for browser-based editing/export)
- A preview of the card structure
- The output location

## Card Design System

The visual cards follow a fixed editorial layout:

```
┌──────────────────────────────────────────┐
│ TOPIC LABEL              SOURCE LABEL    │  ← Top Bar
├────────────────────┬─────────────────────┤
│ English Title      │ Thesis statement    │  ← Title Area
│ 中文标题            │ with key insight    │
├─────┬─────┬─────┬──┴──────────────────────┤
│  M  │  P  │  D  │  G  │                  │  ← Framework Row (2-6 cards)
├─────┴─────┴─────┴─────┴──────────────────┤
│ ⚡ Dark Panel      │ ★ Light Panel        │  ← Two-Column Content
│ (narrative/story)  │ (numbered insights)  │
├──────────────────────────────────────────┤
│ Formula = M × P × D × G    Closing note  │  ← Highlight Bar
├──────────────────────────────────────────┤
│ FRAMEWORK LABEL              BRAND NAME   │  ← Footer
└──────────────────────────────────────────┘
```

### Color Palette

Default theme (customizable):
- Primary: Deep teal `#1a7a6d`
- Accent: Orange `#e8713a`
- Background: Warm gray `#f0ebe4`
- Dark panel: `#1a1a1a`

### Typography

- English display: Playfair Display (serif)
- Chinese body: Noto Sans SC
- Monospace/labels: JetBrains Mono

## Content Strategy

When generating cards from KB content:

1. **Extract or synthesize a framework** - Identify the core structural model (2-6 components)
2. **Create a memorable acronym** - Make the framework easy to remember
3. **Write a provocative thesis** - Strong, opinionated claim in the title area
4. **Dark panel = narrative** - Problems, transitions, paradigm shifts
5. **Light panel = insights** - Actionable numbered takeaways (3-4 items)
6. **Bottom formula** - Distill into one equation-style summary

## Output Format

By default, generate **both** HTML and PNG:

1. **HTML file**: Self-contained with embedded CSS, Google Fonts, and html2canvas for browser export
2. **PNG file**: High-quality render at 1.5× scale (1800px wide), optimized for social media

Output location: `data/cards/YYYY-MM-DD-{topic-slug}/`

## Language Handling

**CRITICAL**: The card content language should match the source KB content language:
- If the KB chapter is in Chinese, generate Chinese card content
- If the KB chapter is in English, generate English card content
- Always include bilingual titles (English + Chinese) regardless of content language
- Technical terms and framework acronyms remain in their original language

## Dependencies

The skill requires:
- Python 3.8+
- Playwright (for PNG rendering): `pip install playwright && playwright install chromium`

Dependencies are checked and installed automatically on first run.

## Resources

- `_scripts/generate_card.py`: Main card generation script
- `_scripts/html2png.py`: Playwright-based HTML to PNG renderer
- `_templates/card_template.html`: Canonical HTML/CSS template
- `_assets/`: Additional assets (if needed)

## Example Usage

```bash
# Generate a card for a specific chapter
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "data/books/markets-and-trading/market-structure-and-signals"

# Generate with custom color scheme
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "data/books/ai-and-research/model-training-and-optimization" \
  --primary-color "#2d5a8c" \
  --accent-color "#d4af37"

# Generate HTML only (skip PNG)
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "data/books/community-qa-and-discussion/platform-discussions" \
  --html-only
```

## Integration with Other Skills

This skill works best after:
- **Synthesis**: Content is already organized in the knowledge base
- **Display**: User has browsed the KB and identified interesting chapters

It can be chained with:
- **Display**: Generate cards for all chapters in a topic
- **Feed**: Create visual cards from feed items

## Notes

- Cards are 1200px wide by default (poster format)
- PNG export uses device-scale-factor for high-DPI rendering
- The floating action button (FAB) in HTML allows browser-based export at multiple resolutions
- All cards include a copyright attribution to the original visual-note-card-skills project
