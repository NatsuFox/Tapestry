# Tapestry Quick Reference

## Installation

```bash
# Install all dependencies (includes browser support)
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Basic Ingestion

```bash
cd skills/tapestry
python3 ingest/_scripts/run.py "https://example.com"
```

### Multiple URLs

```bash
python3 ingest/_scripts/run.py \
  "https://example.com/page1" \
  "https://example.com/page2"
```

### With Context

```bash
python3 ingest/_scripts/run.py \
  --text "Research on AI agents" \
  "https://example.com/article"
```

## Architecture

```
URL → Fetch → Parse → Store
       ↓       ↓       ↓
     HTTP   Selectors  Feed
       ↓       ↓       ↓
   Browser  Readability Note
```

## Extraction Pipeline

1. **HTTP Fetch** - Try standard HTTP request
2. **CSS Selectors** - Extract with configured selectors
3. **Readability** - Fallback content extraction
4. **Browser Rendering** - For JavaScript sites
5. **Metadata** - Last resort (og:description)

## Configuration

### Generic HTML Crawler

```python
fetch=WorkflowFetch(
    mode=FetchMode.http,
    fallback=FetchMode.browser,
)
parse=WorkflowParse(
    title="h1, .title, [class*='title']",
    body="article, main, .content, [role='main']",
)
```

## Output Structure

```
skills/tapestry/
├── data/
│   ├── captures/     # Raw HTML
│   └── feeds/        # Parsed JSON
└── knowledge-base/
    ├── notes/        # Markdown notes
    └── catalog.jsonl # Index
```

## Troubleshooting

### Short content extracted

```
⚠ Extracted content is suspiciously short (70 chars)
→ Enable browser rendering
→ Check CSS selectors
→ Verify readability is installed
```

### Import errors

```bash
# Verify installation
python3 -c "from _src.registry import CrawlerRegistry; print('OK')"

# Check dependencies
pip list | grep -E "httpx|pydantic|selectolax|readability|chardet|playwright"
```

### Browser not working

```bash
# Install browser binaries
playwright install chromium

# Test browser
python3 -c "from playwright.async_api import async_playwright; print('OK')"
```

## Key Files

- `pyproject.toml` - Project configuration
- `requirements.txt` - All dependencies (core + browser + dev)
- `docs/installation.md` - Detailed setup guide
- `docs/improvements.md` - Recent enhancements

## Performance Tips

1. **Use browser rendering selectively** - Only for JS-heavy sites
2. **Batch URLs** - Process multiple URLs in one run
3. **Check duplicates** - System auto-detects duplicate content
4. **Monitor logs** - Watch for short content warnings

## Content Quality

Good extraction indicators:
- ✓ Body length > 500 characters
- ✓ Title extracted
- ✓ Structured content (paragraphs, sections)
- ✓ No "suspiciously short" warnings

Poor extraction indicators:
- ✗ Body length < 200 characters
- ✗ Only metadata description
- ✗ Missing title
- ✗ Warning messages in logs
