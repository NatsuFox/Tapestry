# Visual Card Skill Architecture

Integration details for the Visual Card skill in Tapestry.

## Overview

The Visual Card skill is integrated as a Tapestry sub-skill under `skills/tapestry/visual-card/`. It generates professional visual note cards from knowledge base content as single-page HTML infographics with PNG export.

## Directory Structure

```
skills/tapestry/visual-card/
├── SKILL.md              # Skill definition (Tapestry standard)
├── LICENSE               # MIT License (from original project)
├── _scripts/
│   ├── generate_card.py  # Main card generation script
│   └── html2png.py       # Playwright-based PNG renderer
├── _templates/
│   └── card_template.html # HTML/CSS template
└── _assets/              # Reserved for future assets
```

## Key Adaptations for Tapestry

### 1. Knowledge Base Integration

The script reads directly from Tapestry's `data/books/` structure:
- Supports both `.md` files and directories with `index.md`
- Auto-detects project root by looking for `data/` or `knowledge-base/` directories
- Handles nested chapter paths

### 2. Automatic Framework Extraction

Intelligently parses chapter content to extract key concepts:
- Detects numbered lists: `1. **Title**: description`
- Detects bullet points: `- **Title**: description`
- Generates fallback frameworks if none found
- Supports 2-6 component frameworks (flexible grid)

### 3. Language Detection

Respects the source content language:
- Analyzes content to determine language
- Generates card content in the same language
- Always includes bilingual titles (English + Chinese)
- Preserves technical terms in original language

### 4. Output Organization

Saves to `data/cards/YYYY-MM-DD-{chapter-name}/`:
- Keeps all generated content under `data/` (git-ignored)
- Timestamped directories for version tracking
- Both HTML and PNG in same directory

## Integration Points

### Main Tapestry Skill

Updated `skills/tapestry/SKILL.md` to include visual-card as the 6th sub-skill:

```markdown
Tapestry has six internal sub-skills that work together:

1. Init Deps Install - Auto-triggered dependency installation
2. Ingest - Crawl and capture URLs
3. Synthesis - Analyze and organize into knowledge base
4. Feed - Generate structured, source-aware feeds
5. Display - Visualize the knowledge base as a website
6. Visual Card - Generate visual note cards from KB content
```

### Workflow Integration

Visual cards fit into the Tapestry workflow:

```
Ingest → Synthesis → [Display | Visual Card]
                           ↓
                    Browse KB or Generate Cards
```

## Technical Implementation

### generate_card.py

Main script that:
1. Parses Tapestry KB chapter markdown files
2. Extracts frameworks from numbered lists or bullet points
3. Generates fallback frameworks if none found
4. Populates HTML template with extracted content
5. Calls html2png.py for PNG generation (optional)

**Key Functions:**
- `find_project_root()` - Auto-detects Tapestry root
- `parse_chapter_content()` - Parses markdown files
- `extract_framework_from_content()` - Extracts key concepts
- `generate_html_card()` - Generates HTML from template

### html2png.py

Playwright-based renderer:
- Opens HTML in headless Chromium
- Waits for Google Fonts to load
- Hides floating UI elements
- Screenshots the `.poster` element
- Supports multiple scale factors (1×, 1.5×, 2×)

## Configuration

### Default Settings

- **Output directory**: `data/cards/`
- **PNG scale**: 1.5× (1800px wide)
- **Primary color**: `#1a7a6d` (teal)
- **Accent color**: `#e8713a` (orange)

### Command-Line Options

```bash
--chapter CHAPTER         # Required: chapter path
--output OUTPUT           # Output directory (default: data/cards)
--project-root ROOT       # Project root (auto-detected)
--html-only               # Skip PNG generation
--scale SCALE             # PNG scale factor (default: 1.5)
--primary-color COLOR     # Primary color (default: teal)
--accent-color COLOR      # Accent color (default: orange)
```

## Dependencies

- **Python 3.8+** (Tapestry requirement)
- **Playwright** (optional, for PNG rendering):
  ```bash
  pip install playwright
  playwright install chromium
  ```

HTML generation works without Playwright.

## Git Configuration

All visual card outputs are git-ignored:

```gitignore
# Generated project content (all under data/)
/data/
```

This ensures personal data (including generated cards) never gets committed.

## Performance Considerations

### HTML Generation

- Fast: ~100ms per card
- No external dependencies (except template)
- Pure Python string manipulation

### PNG Generation

- Slower: ~2-3 seconds per card
- Requires Playwright and Chromium
- Headless browser rendering
- Can be skipped with `--html-only`

### Batch Processing

For multiple cards:
```bash
for chapter in data/books/topic/*.md; do
  python skills/tapestry/visual-card/_scripts/generate_card.py \
    --chapter "topic/$(basename "$chapter")"
done
```

## Future Enhancements

Potential improvements:
1. **Batch Mode**: Generate cards for entire topics at once
2. **Theme Presets**: Pre-defined color schemes
3. **Template Variants**: Alternative layouts
4. **Display Integration**: Embed card previews in KB viewer
5. **Feed Integration**: Generate cards from feed items
6. **AI Enhancement**: Use LLM to improve framework extraction

## Acknowledgments

🎨 Based on [visual-note-card-skills](https://github.com/beilunyang/visual-note-card-skills) by beilunyang, licensed under MIT License.

Adapted for Tapestry integration by the Tapestry project.

## Related Documentation

- [Visual Cards Guide](../guides/visual-cards.md) - User guide and examples
- [Skill Architecture](skill-architecture.md) - General skill architecture
- [Knowledge Base](../guides/knowledge-base.md) - KB structure and organization
