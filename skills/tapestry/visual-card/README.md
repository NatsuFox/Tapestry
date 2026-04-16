# Tapestry Visual Card

Generate professional visual note cards from Tapestry knowledge base content.

## Quick Start

```bash
# Generate a card from a KB chapter
python skills/tapestry/visual-card/_scripts/generate_card.py \
  --chapter "ai-and-development-tools/ai-agent-architecture.md"
```

## Documentation

The repository keeps extended working docs local-only. The tracked references for this skill are:

- **[SKILL.md](SKILL.md)** - Skill definition and workflow
- **[README.en.md](../../../README.en.md)** - Repository overview, installation, and visual frontend context
- **`visual-card/_templates/card_template_spec.md`** - Template block specification used during synthesis

## Features

- **Knowledge Base Integration**: Directly reads from Tapestry's `data/books/` structure
- **Automatic Framework Extraction**: Intelligently extracts key concepts and structures
- **Bilingual Support**: Chinese body text with English display titles
- **Multiple Export Formats**: Self-contained HTML + high-quality PNG
- **Customizable Themes**: Configurable color schemes
- **Browser Export**: Built-in FAB with multiple resolution options

## Output

Generated files are saved to `data/cards/YYYY-MM-DD-{chapter-name}/`:
- `{chapter-name}.html` - Self-contained HTML with embedded styles
- `{chapter-name}.png` - High-quality PNG (1.5× scale by default)

## Dependencies

- Python 3.8+
- Playwright (for PNG rendering): `pip install playwright && playwright install chromium`

## Acknowledgments

🎨 Based on [visual-note-card-skills](https://github.com/beilunyang/visual-note-card-skills) by beilunyang.
Licensed under MIT License (see LICENSE file).
