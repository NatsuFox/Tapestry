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

### Architecture: Agent-Driven Content Synthesis

This skill uses an **Agent-driven approach** where the Agent reads the template specification and autonomously decides how to map source content to template blocks.

**Key principle**: The template structure is fixed (7 display blocks), but content mapping is intelligent and adaptive.

### Step 1: Identify the Source Content

Resolve the target from the argument:
- If a specific chapter path is provided (e.g., "ai-and-development-tools/ai-agent-architecture.md"), use that chapter
- If a topic is provided (e.g., "ai-and-development-tools"), offer to generate cards for its chapters
- If no argument, list available topics and ask the user to choose

```bash
# List available topics
ls -d data/books/*/
```

### Step 2: Prepare Context for Agent

The `prepare_card_context.py` script extracts:
- Source content (markdown with frontmatter)
- Template specification (natural language description of 7 blocks)
- Instructions for the Agent

This creates a JSON context that the Agent will analyze.

### Step 3: Agent Synthesizes Content Mapping

The Agent reads:
1. **Template specification** (`_templates/card_template_spec.md`) - describes what each block is for, quality criteria, examples
2. **Source content** - the actual KB chapter markdown
3. **Instructions** - task description and guidelines

The Agent then autonomously decides:
- What framework structure best represents the content (2-6 components)
- Which insights are most valuable and provocative
- How to organize narrative flow in the dark panel
- What thesis statement captures the core argument
- How to create a memorable closing thought

**Output**: A synthesis JSON with all 7 blocks filled with intelligent content selections.

### Step 4: Generate HTML/PNG from Synthesis

The `generate_card_from_synthesis.py` script takes the Agent's synthesis JSON and:
1. Loads the HTML template
2. Fills all placeholders with synthesized content
3. Generates the final HTML card
4. Renders PNG using Playwright

### Step 5: Present the Results

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

- `_scripts/generate_card.py`: Main orchestrator for Agent-driven workflow
- `_scripts/prepare_card_context.py`: Prepares context (source + template spec) for Agent
- `_scripts/generate_card_from_synthesis.py`: Generates HTML/PNG from Agent synthesis
- `_scripts/html2png.py`: Playwright-based HTML to PNG renderer
- `_scripts/generate_card_legacy.py`: Legacy hardcoded extraction (fallback)
- `_templates/card_template.html`: Canonical HTML/CSS template
- `_templates/card_template_spec.md`: Natural language specification for Agent (describes 7 blocks, quality criteria, examples)
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
