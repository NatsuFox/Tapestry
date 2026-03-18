# Visual Cards

Generate professional visual note cards from your knowledge base content.

## Overview

The Visual Card skill transforms structured knowledge base chapters into beautiful, information-dense visual cards following an editorial magazine aesthetic. Perfect for social media sharing, presentations, or visual summaries.

## Quick Start

```bash
# Generate a card from a KB chapter
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "ai-and-development-tools/ai-agent-architecture.md"
```

This creates both:
- `data/cards/2026-03-18-ai-agent-architecture.md/ai-agent-architecture.md.html`
- `data/cards/2026-03-18-ai-agent-architecture.md/ai-agent-architecture.md.png`

## Card Layout

Visual cards follow a fixed poster structure (1200px wide):

```
┌──────────────────────────────────────────┐
│ TOPIC LABEL              SOURCE LABEL    │  ← Top Bar
├────────────────────┬─────────────────────┤
│ English Title      │ Thesis statement    │  ← Title Area
│ 中文标题            │ with key insight    │
├─────┬─────┬─────┬──┴──────────────────────┤
│  C  │  M  │  I  │  A  │                  │  ← Framework Row (2-6 cards)
├─────┴─────┴─────┴─────┴──────────────────┤
│ ⚡ Dark Panel      │ ★ Light Panel        │  ← Two-Column Content
│ (narrative/story)  │ (numbered insights)  │
├──────────────────────────────────────────┤
│ Formula = C × M × I × A    Closing note  │  ← Highlight Bar
├──────────────────────────────────────────┤
│ FRAMEWORK LABEL              TAPESTRY    │  ← Footer
└──────────────────────────────────────────┘
```

## Usage Examples

### Basic Card Generation

```bash
# From a specific chapter
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "ai-and-development-tools/ai-agent-architecture.md"
```

### Custom Colors

```bash
# Blue and gold theme
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "markets-and-trading/market-structure-and-signals" \
  --primary-color "#2d5a8c" \
  --accent-color "#d4af37"
```

### HTML Only (Skip PNG)

```bash
# Generate HTML for browser editing
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "community-qa-and-discussion/platform-discussions" \
  --html-only
```

### High Resolution

```bash
# 2× scale for printing
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "general-reference/reference-and-articles" \
  --scale 2.0
```

## Integration with Tapestry Workflow

### After Synthesis

```bash
# 1. Ingest content
python skills/tapestry/ingest/_scripts/run.py "https://example.com/article"

# 2. Synthesis runs automatically (if in "auto" mode)
# Content is organized into data/books/

# 3. Generate visual card
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "ai-and-development-tools/research-tracking-and-papers"
```

### Batch Card Generation

Generate cards for all chapters in a topic:

```bash
for chapter in data/books/ai-and-development-tools/*.md; do
  chapter_name=$(basename "$chapter" .md)
  python skills/tapestry/visual-card/_scripts/generate_card.py \
    --chapter "ai-and-development-tools/$chapter_name.md"
done
```

## Content Strategy

The card generator intelligently extracts content from your KB chapters:

1. **Framework Extraction**: Automatically identifies 2-6 key components from numbered lists or bullet points
2. **Insight Generation**: Extracts 3-4 key takeaways from the content
3. **Fallback Frameworks**: Creates sensible defaults if no clear structure is found
4. **Language Detection**: Respects the source content language (Chinese/English)

## Design System

### Color Palette

Default theme (customizable):
- **Primary**: Deep teal `#1a7a6d` - headers, badges, accents
- **Accent**: Orange `#e8713a` - emphasis, secondary badges
- **Background**: Warm gray `#f0ebe4` - page background
- **Dark panel**: `#1a1a1a` - narrative content

### Typography

- **English display**: Playfair Display (serif) - main titles
- **Chinese body**: Noto Sans SC - all Chinese text
- **Monospace**: JetBrains Mono - labels, URLs, tags

All fonts loaded via Google Fonts CDN.

## Output Format

### HTML File

Self-contained HTML with:
- Embedded CSS styles
- Google Fonts integration
- html2canvas for browser export
- Floating action button (FAB) with export options:
  - Standard PNG (1×)
  - HD PNG (1.5×) - recommended for social media
  - Ultra HD PNG (2×) - for printing
  - JPEG (1.5×) - smaller file size

### PNG File

High-quality render via Playwright:
- Default: 1.5× scale (1800px wide)
- Optimized for social media sharing
- No floating UI elements (clean export)

## Dependencies

- **Python 3.8+** (already required by Tapestry)
- **Playwright** (for PNG rendering):
  ```bash
  pip install playwright
  playwright install chromium
  ```

Note: HTML generation works without Playwright. PNG generation requires it.

## Advanced Usage

### Custom Output Directory

```bash
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "ai-and-development-tools/ai-agent-architecture.md" \
  --output "custom/output/path"
```

### Specify Project Root

```bash
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "ai-and-development-tools/ai-agent-architecture.md" \
  --project-root "/path/to/tapestry"
```

## Troubleshooting

### "Chapter not found"

The script looks for chapters in these locations (in order):
1. `data/books/{chapter-path}`
2. `knowledge-base/books/{chapter-path}`
3. Absolute path provided

Ensure your chapter path is relative to one of these directories.

### "No markdown file found"

The script looks for:
1. `{chapter-path}/index.md` (directory with index)
2. `{chapter-path}.md` (direct markdown file)
3. `{chapter-path}` (if already a file)

### PNG Generation Fails

If Playwright is not installed:
```bash
pip install playwright
playwright install chromium
```

Or use `--html-only` to skip PNG generation.

### Framework Not Extracted

The generator looks for:
- Numbered lists with bold headers: `1. **Title**: description`
- Bullet points with bold headers: `- **Title**: description`

If not found, it creates a default 4-component framework (Concept, Method, Insight, Application).

## Best Practices

1. **Organize KB First**: Ensure your knowledge base chapters are well-structured before generating cards
2. **Use Numbered Lists**: Format key concepts as numbered lists for better framework extraction
3. **Bold Key Terms**: Use `**bold**` for important terms to help extraction
4. **Test HTML First**: Use `--html-only` to quickly preview before generating PNG
5. **Batch Processing**: Generate cards for entire topics at once for consistency

## Acknowledgments

🎨 Based on [visual-note-card-skills](https://github.com/beilunyang/visual-note-card-skills) by beilunyang, licensed under MIT License.

Adapted for Tapestry integration with:
- Knowledge base integration
- Automatic framework extraction
- Language detection
- Project-aware path resolution
