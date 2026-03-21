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

### Step 2: Run the Context Preparation Script

```bash
python visual-card/_scripts/generate_card.py --chapter "<topic>/<chapter.md>"
```

This prints a JSON object with three keys:
- `source.content`: the raw chapter markdown
- `source.frontmatter`: parsed metadata (title, author, date, etc.)
- `template_specification`: full natural language spec of the 7 template blocks
- `instructions`: task description

### Step 3: Read the Template Specification

Read `visual-card/_templates/card_template_spec.md` to understand:
- What each of the 7 blocks is for
- Quality criteria for content selection
- Expected JSON output format with examples

### Step 4: Synthesize the Content Mapping (Agent Task)

Analyze the source content against the template spec and produce a synthesis JSON. Write it to a temp file:

```bash
# Write synthesis to temp file
cat > /tmp/card_synthesis.json << 'EOF'
{
  "metadata": {
    "chapter": "<chapter-name>",
    "title_en": "<English title, 3-8 words>",
    "title_cn": "<Chinese title>",
    "topic_label": "<TOPIC LABEL IN CAPS>",
    "source_label": "<SOURCE IN CAPS>",
    "thesis": "<one sentence with <strong>keyword</strong> embedded>"
  },
  "framework": {
    "formula": "<A × B × C format>",
    "formula_subtext": "<what the formula means>",
    "label": "<FRAMEWORK NAME>",
    "components": [
      {"letter": "A", "name": "Component Name", "description": "One-line description"}
    ]
  },
  "insights": [
    {"number": "01", "title": "Insight Title", "description": "2-3 sentence insight description"}
  ],
  "dark_panel": {
    "icon": "⚡",
    "section_title": "<Section Title>",
    "block1": {"title": "<Block 1 Title>", "items": ["item 1", "item 2", "item 3"]},
    "block2": {"title": "<Block 2 Title>", "items": ["item 1", "item 2", "item 3", "item 4"]},
    "conclusion": {"label": "核心洞察", "text": "<conclusion text>", "highlight": "<highlighted phrase>"}
  },
  "closing_thought": {
    "text": "<memorable closing insight>",
    "attribution": "<author or source>"
  }
}
EOF
```

Content decisions to make:
- **Framework**: Identify 2-6 core concepts that structure the topic (acronym or logical grouping)
- **Insights**: Select 3-5 most surprising, actionable, or paradigm-shifting points
- **Dark panel**: Narrative flow — overview → key mechanics → conclusion
- **Thesis**: A single provocative claim that captures the article's core argument
- **Closing thought**: A memorable synthesis that gives the reader something to carry away

### Step 5: Generate HTML/PNG from Synthesis

```bash
python visual-card/_scripts/generate_card_from_synthesis.py \
  --synthesis /tmp/card_synthesis.json \
  --chapter "<topic>/<chapter.md>"
```

This renders the synthesis into the HTML template and exports PNG via Playwright.

### Step 6: Present the Results

Report back with:
- The generated PNG path (primary deliverable)
- The HTML path (for browser-based editing/export)
- A brief summary of the content mapping decisions made

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

- `visual-card/_scripts/generate_card.py`: Main orchestrator for Agent-driven workflow
- `visual-card/_scripts/prepare_card_context.py`: Prepares context (source + template spec) for Agent
- `visual-card/_scripts/generate_card_from_synthesis.py`: Generates HTML/PNG from Agent synthesis
- `visual-card/_scripts/html2png.py`: Playwright-based HTML to PNG renderer
- `visual-card/_scripts/generate_card_legacy.py`: Legacy hardcoded extraction (fallback)
- `visual-card/_templates/card_template.html`: Canonical HTML/CSS template
- `visual-card/_templates/card_template_spec.md`: Natural language specification for Agent (describes 7 blocks, quality criteria, examples)
- `_assets/`: Additional assets (if needed)

## Example Usage

```bash
# Generate a card for a specific chapter
python visual-card/_scripts/generate_card.py \
  --chapter "data/books/markets-and-trading/market-structure-and-signals"

# Generate with custom color scheme
python visual-card/_scripts/generate_card.py \
  --chapter "data/books/ai-and-research/model-training-and-optimization" \
  --primary-color "#2d5a8c" \
  --accent-color "#d4af37"

# Generate HTML only (skip PNG)
python visual-card/_scripts/generate_card.py \
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
