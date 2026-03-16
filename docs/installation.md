# Installation Guide

## Quick Start

### Option 1: Using pip with requirements.txt

```bash
# Install all dependencies (includes browser support)
pip install -r requirements.txt

# After installing playwright, install browser binaries
playwright install chromium
```

**Note**: The requirements.txt includes browser rendering support by default. To skip browser support, comment out the `playwright` line before installing.

### Option 2: Using pyproject.toml

```bash
# Install core dependencies only
pip install -e .

# Install with browser support
pip install -e ".[browser]"

# Install with all features including dev tools
pip install -e ".[all]"

# After installing playwright, install browser binaries
playwright install chromium
```

## Dependencies

### Core Dependencies (Required)

- **httpx** (>=0.27.0) - Async HTTP client for fetching web pages
- **pydantic** (>=2.0.0) - Data validation and structured models
- **selectolax** (>=0.3.0) - Fast HTML parsing with CSS selectors
- **readability-lxml** (>=0.8.0) - Content extraction fallback for complex HTML
- **chardet** (>=5.0.0) - Character encoding detection

### Optional Dependencies

#### Browser Rendering (Recommended)

- **playwright** (>=1.40.0) - Headless browser for JavaScript-heavy sites

Browser rendering is **highly recommended** for modern web applications that rely on JavaScript. Without it, you'll only get server-side HTML which may be incomplete.

After installing playwright:
```bash
playwright install chromium
```

### Development Dependencies

- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage
- **black** - Code formatter
- **ruff** - Fast Python linter
- **mypy** - Static type checker

## Verification

Test your installation:

```bash
python3 -c "
from _src.registry import CrawlerRegistry
from _src.ingest import IngestionService
print('✓ Core dependencies installed')

try:
    from playwright.async_api import async_playwright
    print('✓ Browser rendering available')
except ImportError:
    print('⚠ Browser rendering not available (optional)')
"
```

## Troubleshooting

### Missing chardet

If you see errors about `chardet` or `cchardet`:
```bash
pip install chardet
```

### Playwright browser not found

If you get "Executable doesn't exist" errors:
```bash
playwright install chromium
```

### Import errors

Make sure you're in the correct directory:
```bash
cd skills/tapestry
python3 -c "from _src.registry import CrawlerRegistry; print('OK')"
```

## Platform-Specific Notes

### Linux

Playwright may require additional system dependencies:
```bash
# Debian/Ubuntu
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

### macOS

No additional dependencies required.

### Windows

Playwright should work out of the box after `playwright install chromium`.

## Minimal Installation (No Browser)

If you don't need browser rendering:

```bash
pip install httpx pydantic selectolax readability-lxml chardet
```

This will work for:
- Static HTML pages
- Server-side rendered content
- Sites with good semantic HTML

But will fail for:
- Single-page applications (SPAs)
- JavaScript-rendered content
- Modern documentation sites (like Mintlify, Docusaurus, etc.)
