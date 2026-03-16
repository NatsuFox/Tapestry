# Configuration Reference

Complete reference for configuring Tapestry crawlers, pipelines, workflows, and synthesis behavior.

## Configuration Overview

Tapestry uses two configuration approaches:

1. **Runtime Configuration** (`tapestry.config.json`): Controls synthesis modes, default crawlers, and paths
2. **Code-Based Configuration**: Crawler definitions, workflow profiles, and parsing rules

## Runtime Configuration (tapestry.config.json)

### Configuration File Location

Place the configuration file at your project root:
```
<project-root>/tapestry.config.json
```

If no configuration file exists, Tapestry uses sensible defaults.

### Configuration Schema

```json
{
  "synthesis": {
    "mode": "auto",
    "description": "Controls when synthesis runs after ingestion"
  },
  "ingest": {
    "default_crawler": "auto",
    "description": "Default crawler to use"
  },
  "paths": {
    "project_root": ".",
    "data_dir": "data",
    "knowledge_base_dir": "knowledge-base"
  }
}
```

### Synthesis Mode

**Field**: `synthesis.mode`
**Type**: `"auto" | "manual" | "batch"`
**Default**: `"auto"`

Controls when synthesis runs after content ingestion:

#### `"auto"` (Recommended)
- Synthesis runs automatically after each successful ingest
- Best for: Real-time knowledge base building
- Workflow: Ingest URL → Synthesize immediately → Organized in book structure

**Example**:
```bash
$tapestry-ingest https://example.com/article
# Automatically triggers synthesis and organizes into KB
```

#### `"manual"`
- Synthesis only runs when explicitly invoked
- Best for: Batch capture now, organize later
- Workflow: Ingest URLs → Review notes → Selectively synthesize

**Example**:
```bash
# Capture multiple URLs quickly
$tapestry-ingest https://example.com/article1
$tapestry-ingest https://example.com/article2

# Later, synthesize selectively
$tapestry-synthesis https://example.com/article1
```

#### `"batch"`
- Ingest multiple URLs, then synthesize all at once
- Best for: Bulk processing with single synthesis pass
- Workflow: Ingest many URLs → Synthesize all together

### Default Crawler

**Field**: `ingest.default_crawler`
**Type**: `string`
**Default**: `"auto"`

Specifies which crawler to use by default:

- `"auto"`: Automatically detect based on URL pattern (recommended)
- `"generic_html"`: Force generic HTML crawler
- `"zhihu"`, `"reddit"`, `"hackernews"`, etc.: Force specific platform crawler

### Paths Configuration

**Fields**: `paths.project_root`, `paths.data_dir`, `paths.knowledge_base_dir`
**Type**: `string`
**Defaults**: `"."`, `"data"`, `"knowledge-base"`

Configure directory locations (relative to project root).

## Code-Based Configuration

## Crawler Configuration

### Fetch Configuration

Control how content is fetched from URLs.

#### WorkflowFetch

```python
from _src.base import WorkflowFetch, FetchMode

fetch = WorkflowFetch(
    mode=FetchMode.http,           # Primary fetch method
    fallback=FetchMode.browser,    # Fallback if primary fails
    timeout=30,                     # Request timeout (seconds)
    headers={                       # Custom HTTP headers
        "User-Agent": "Tapestry/1.0",
        "Accept-Language": "en-US,en;q=0.9",
    },
    retry_count=3,                  # Number of retries
    retry_delay=1,                  # Delay between retries (seconds)
)
```

#### Fetch Modes

**FetchMode.http**
- Standard HTTP request
- Fast (< 1 second)
- No JavaScript execution
- Low resource usage

```python
fetch = WorkflowFetch(mode=FetchMode.http)
```

**FetchMode.browser**
- Full browser rendering
- Slow (3-10 seconds)
- JavaScript execution
- High resource usage

```python
fetch = WorkflowFetch(mode=FetchMode.browser)
```

**FetchMode.http with browser fallback**
- Try HTTP first
- Fall back to browser if needed
- Best of both worlds

```python
fetch = WorkflowFetch(
    mode=FetchMode.http,
    fallback=FetchMode.browser,
)
```

### Parse Configuration

Control how content is extracted from HTML.

#### WorkflowParse

```python
from _src.base import WorkflowParse

parse = WorkflowParse(
    title="h1, .title, [class*='title']",     # Title selectors
    body="article, main, .content",            # Body selectors
    author=".author-name, .byline",            # Author selectors
    timestamp=".publish-date, time",           # Timestamp selectors
    readability_fallback=True,                 # Enable readability
    metadata_fallback=True,                    # Enable metadata extraction
)
```

#### CSS Selectors

**Multiple selectors** (comma-separated):
```python
title="h1, .title, [class*='title']"
# Tries each selector in order until one matches
```

**Descendant selectors**:
```python
body="article .content, main .post-body"
# Matches .content inside article, or .post-body inside main
```

**Attribute selectors**:
```python
author="[data-author], [class*='author']"
# Matches elements with data-author attribute or class containing 'author'
```

#### Readability Fallback

Automatically extract content using Mozilla's Readability algorithm:

```python
parse = WorkflowParse(
    title="h1",
    body="article",
    readability_fallback=True,  # Enable fallback
)
```

**When it activates**:
- CSS selectors return no content
- Content is too short (< 200 chars)

#### Metadata Fallback

Extract from Open Graph and meta tags:

```python
parse = WorkflowParse(
    title="h1",
    body="article",
    metadata_fallback=True,  # Enable fallback
)
```

**Extracted fields**:
- `og:title` → title
- `og:description` → body
- `og:author` → author
- `article:published_time` → timestamp

## Platform-Specific Configuration

### Zhihu Crawler

```python
# _src/crawlers/zhihu/__init__.py

class ZhihuAnswerCrawler(BaseCrawler):
    fetch = WorkflowFetch(
        mode=FetchMode.http,
        timeout=30,
    )

    parse = WorkflowParse(
        title=".QuestionHeader-title",
        body=".RichContent-inner",
        author=".AuthorInfo-name",
        timestamp=".ContentItem-time",
    )
```

### Reddit Crawler

```python
# _src/crawlers/reddit/__init__.py

class RedditCrawler(BaseCrawler):
    fetch = WorkflowFetch(
        mode=FetchMode.http,
        timeout=30,
    )

    parse = WorkflowParse(
        title='[slot="title"]',
        body='[slot="text-body"]',
        author='[slot="authorName"]',
    )
```

### Generic HTML Crawler

```python
# _src/crawlers/generic_html/__init__.py

class GenericHTMLCrawler(BaseCrawler):
    fetch = WorkflowFetch(
        mode=FetchMode.http,
        fallback=FetchMode.browser,  # Fallback for JS sites
        timeout=30,
    )

    parse = WorkflowParse(
        title="h1, .title, [class*='title']",
        body="article, main, .content, [role='main']",
        author=".author, .byline, [rel='author']",
        readability_fallback=True,
        metadata_fallback=True,
    )
```

## Validation Configuration

### Content Quality Validation

```python
# _src/parse.py

MIN_BODY_LENGTH = 200  # Minimum body length (chars)
WARN_THRESHOLD = 200   # Warn if below this length

def validate_content(content: dict) -> bool:
    body = content.get("body", "")

    if len(body) < WARN_THRESHOLD:
        logger.warning(
            f"Extracted content is suspiciously short ({len(body)} chars). "
            "Consider using browser rendering."
        )

    return True  # Continue even with warnings
```

**Customization**:
```python
# Adjust thresholds
MIN_BODY_LENGTH = 500   # Stricter minimum
WARN_THRESHOLD = 1000   # Higher warning threshold
```

## Registry Configuration

### Crawler Registry

```python
# _src/registry.py

CRAWLER_REGISTRY = {
    "zhihu_answer": {
        "patterns": [r"zhihu\.com/question/.*/answer/.*"],
        "crawler": ZhihuAnswerCrawler,
        "priority": 10,  # Higher priority = checked first
    },
    "generic_html": {
        "patterns": [r".*"],  # Matches everything
        "crawler": GenericHTMLCrawler,
        "priority": 0,  # Lowest priority (fallback)
    },
}
```

**Adding a new crawler**:
```python
CRAWLER_REGISTRY["myplatform"] = {
    "patterns": [r"myplatform\.com/.*"],
    "crawler": MyPlatformCrawler,
    "priority": 5,
}
```

## Storage Configuration

### File Paths

```python
# Default paths
CAPTURES_DIR = "data/captures/"
FEEDS_DIR = "data/feeds/"
KNOWLEDGE_BASE_DIR = "knowledge-base/"

# Customize paths
import os
os.environ["TAPESTRY_CAPTURES_DIR"] = "/custom/path/captures/"
os.environ["TAPESTRY_FEEDS_DIR"] = "/custom/path/feeds/"
os.environ["TAPESTRY_KB_DIR"] = "/custom/path/kb/"
```

### File Naming

```python
# Default format: {timestamp}_{platform}_{content_type}_{id}.{ext}
# Example: 20260316T103000Z_zhihu_answer_123456.json

# Customize format
def generate_filename(content: dict) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    platform = content["platform"]
    content_type = content["content_type"]
    content_id = content.get("id", "unknown")

    return f"{timestamp}_{platform}_{content_type}_{content_id}"
```

## Browser Configuration

### Playwright Settings

```python
# _src/fetch.py

async def browser_fetch(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,              # Run without GUI
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 ...",
            locale="en-US",
        )

        page = await context.new_page()

        await page.goto(url, wait_until="networkidle", timeout=30000)

        html = await page.content()

        await browser.close()

        return html
```

**Customization options**:

```python
# Use different browser
browser = await p.firefox.launch()

# Disable images (faster)
context = await browser.new_context(
    bypass_csp=True,
    ignore_https_errors=True,
)

# Set custom viewport
context = await browser.new_context(
    viewport={"width": 1280, "height": 720},
)

# Wait for specific element
await page.wait_for_selector(".content", timeout=10000)
```

## Synthesis Configuration

### Knowledge Base Structure

```python
# synthesis/_kb_blueprint/

# Define topic taxonomy
TOPICS = {
    "ai-and-research": {
        "name": "AI and Research",
        "chapters": [
            "research-tracking-and-papers",
            "model-training-and-optimization",
        ],
    },
    "community-qa-and-discussion": {
        "name": "Community Q&A and Discussion",
        "chapters": [
            "platform-discussions",
            "practical-identification-and-qa",
        ],
    },
}
```

### Chapter Decision Rules

```python
# synthesis/_kb_rules/chapter-decision-rules.md

# Define rules for chapter selection
RULES = """
- Academic papers → research-tracking-and-papers
- Training guides → model-training-and-optimization
- Forum discussions → platform-discussions
- How-to questions → practical-identification-and-qa
"""
```

## Logging Configuration

### Log Levels

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Available levels:
# - DEBUG: Detailed information
# - INFO: General information
# - WARNING: Warning messages
# - ERROR: Error messages
# - CRITICAL: Critical errors
```

### Custom Logging

```python
# Configure custom logger
import logging

logger = logging.getLogger("tapestry")
logger.setLevel(logging.DEBUG)

# Add file handler
handler = logging.FileHandler("tapestry.log")
handler.setLevel(logging.DEBUG)

# Add formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)
```

## Environment Variables

### Available Variables

```bash
# Storage paths
export TAPESTRY_CAPTURES_DIR="/custom/captures"
export TAPESTRY_FEEDS_DIR="/custom/feeds"
export TAPESTRY_KB_DIR="/custom/kb"

# Fetch settings
export TAPESTRY_FETCH_TIMEOUT=60
export TAPESTRY_FETCH_RETRIES=5

# Browser settings
export TAPESTRY_BROWSER_HEADLESS=true
export TAPESTRY_BROWSER_TIMEOUT=60000

# Validation settings
export TAPESTRY_MIN_BODY_LENGTH=500
export TAPESTRY_WARN_THRESHOLD=1000

# Logging
export TAPESTRY_LOG_LEVEL=DEBUG
export TAPESTRY_LOG_FILE="tapestry.log"
```

### Loading from .env

```bash
# Create .env file
cat > .env <<EOF
TAPESTRY_CAPTURES_DIR=/custom/captures
TAPESTRY_FETCH_TIMEOUT=60
TAPESTRY_LOG_LEVEL=DEBUG
EOF

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

## Performance Tuning

### HTTP Client Settings

```python
import httpx

# Configure client
client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(
        max_keepalive_connections=10,
        max_connections=20,
    ),
    follow_redirects=True,
)
```

### Browser Pool

```python
# Reuse browser instances
class BrowserPool:
    def __init__(self, size=3):
        self.size = size
        self.browsers = []

    async def get_browser(self):
        if len(self.browsers) < self.size:
            browser = await p.chromium.launch()
            self.browsers.append(browser)
        return self.browsers[0]  # Round-robin
```

### Caching

```python
# Enable caching
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_cached(url: str) -> str:
    return fetch(url)
```

## Security Configuration

### User Agent

```python
# Set custom user agent
headers = {
    "User-Agent": "Tapestry/1.0 (https://github.com/user/tapestry)",
}
```

### Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.rpm = requests_per_minute
        self.requests = []

    async def acquire(self):
        now = datetime.now()
        self.requests = [r for r in self.requests if now - r < timedelta(minutes=1)]

        if len(self.requests) >= self.rpm:
            wait = 60 - (now - self.requests[0]).seconds
            await asyncio.sleep(wait)

        self.requests.append(now)
```

### Robots.txt Compliance

```python
from urllib.robotparser import RobotFileParser

def can_fetch(url: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(f"{url.scheme}://{url.netloc}/robots.txt")
    rp.read()
    return rp.can_fetch("Tapestry", url)
```

## Examples

### Custom Crawler

```python
# _src/crawlers/myplatform/__init__.py

from ..base import BaseCrawler, WorkflowFetch, WorkflowParse, FetchMode

class MyPlatformCrawler(BaseCrawler):
    """Crawler for MyPlatform"""

    fetch = WorkflowFetch(
        mode=FetchMode.http,
        fallback=FetchMode.browser,
        timeout=30,
        headers={
            "User-Agent": "Tapestry/1.0",
        },
    )

    parse = WorkflowParse(
        title=".post-title, h1",
        body=".post-content, article",
        author=".author-name",
        timestamp=".publish-date",
        readability_fallback=True,
    )
```

### Custom Validation

```python
# _src/parse.py

def validate_content(content: dict) -> bool:
    # Check title
    if not content.get("title"):
        logger.error("Missing title")
        return False

    # Check body length
    body = content.get("body", "")
    if len(body) < 500:
        logger.warning(f"Short content: {len(body)} chars")

    # Check for spam indicators
    if "buy now" in body.lower():
        logger.warning("Possible spam content")

    return True
```

## Best Practices

### Configuration Management

**Use version control**:
- Commit configuration changes
- Document why changes were made
- Test before deploying

**Use environment variables for secrets**:
- API keys
- Credentials
- Sensitive paths

**Keep defaults sensible**:
- Work for most use cases
- Document when to customize

### Performance

**Start with HTTP**:
- Only use browser when needed
- Test if HTTP works first

**Tune timeouts**:
- Balance speed vs reliability
- Adjust based on target sites

**Monitor resource usage**:
- Watch memory with browser rendering
- Limit concurrent operations

## Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for configuration-related issues.

## Next Steps

- Learn about [Crawler System](../architecture/crawlers.md)
- Explore [Content Pipeline](../architecture/content-pipeline.md)
- Read [Advanced Workflows](../guides/advanced-workflows.md)
