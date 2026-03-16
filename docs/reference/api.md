# API Reference

Python API reference for Tapestry's core components.

## Overview

Tapestry provides a Python API for programmatic access to crawling, parsing, and knowledge base management.

## Core Modules

### _src.registry

Crawler registry and URL routing.

#### CrawlerRegistry

```python
from _src.registry import CrawlerRegistry

registry = CrawlerRegistry()
```

**Methods**:

##### get_crawler(url: str) → BaseCrawler

Get appropriate crawler for a URL.

```python
crawler = registry.get_crawler("https://www.zhihu.com/question/123/answer/456")
# Returns: ZhihuAnswerCrawler instance
```

**Parameters**:
- `url` (str): URL to match

**Returns**:
- `BaseCrawler`: Crawler instance

**Raises**:
- `ValueError`: If no crawler matches URL

##### register_crawler(name: str, patterns: list, crawler: type, priority: int = 5)

Register a new crawler.

```python
registry.register_crawler(
    name="myplatform",
    patterns=[r"myplatform\.com/.*"],
    crawler=MyPlatformCrawler,
    priority=5,
)
```

**Parameters**:
- `name` (str): Crawler identifier
- `patterns` (list[str]): Regex patterns to match URLs
- `crawler` (type): Crawler class
- `priority` (int): Priority (higher = checked first)

### _src.ingest

Content ingestion service.

#### IngestionService

```python
from _src.ingest import IngestionService

service = IngestionService()
```

**Methods**:

##### async ingest(url: str, context: str = None) → dict

Ingest content from a URL.

```python
result = await service.ingest(
    url="https://example.com/article",
    context="Research on AI agents",
)
```

**Parameters**:
- `url` (str): URL to ingest
- `context` (str, optional): Context for organization

**Returns**:
- `dict`: Ingestion result with keys:
  - `capture_path` (str): Path to raw HTML
  - `feed_path` (str): Path to structured JSON
  - `content` (dict): Extracted content

**Raises**:
- `FetchError`: If fetching fails
- `ParseError`: If parsing fails

##### async ingest_batch(urls: list, context: str = None) → list

Ingest multiple URLs.

```python
results = await service.ingest_batch(
    urls=[
        "https://example.com/page1",
        "https://example.com/page2",
    ],
    context="Research collection",
)
```

**Parameters**:
- `urls` (list[str]): URLs to ingest
- `context` (str, optional): Context for organization

**Returns**:
- `list[dict]`: List of ingestion results

### _src.fetch

Content fetching.

#### fetch_http(url: str, timeout: int = 30, headers: dict = None) → str

Fetch content via HTTP.

```python
from _src.fetch import fetch_http

html = await fetch_http(
    url="https://example.com",
    timeout=30,
    headers={"User-Agent": "Tapestry/1.0"},
)
```

**Parameters**:
- `url` (str): URL to fetch
- `timeout` (int): Request timeout in seconds
- `headers` (dict, optional): Custom HTTP headers

**Returns**:
- `str`: HTML content

**Raises**:
- `httpx.HTTPError`: If request fails

#### fetch_browser(url: str, timeout: int = 30000) → str

Fetch content via browser rendering.

```python
from _src.fetch import fetch_browser

html = await fetch_browser(
    url="https://spa-site.com",
    timeout=30000,
)
```

**Parameters**:
- `url` (str): URL to fetch
- `timeout` (int): Timeout in milliseconds

**Returns**:
- `str`: Rendered HTML content

**Raises**:
- `playwright.Error`: If browser operation fails

### _src.parse

Content parsing and extraction.

#### parse_with_selectors(html: str, selectors: dict) → dict

Parse HTML using CSS selectors.

```python
from _src.parse import parse_with_selectors

content = parse_with_selectors(
    html=html,
    selectors={
        "title": "h1, .title",
        "body": "article, main",
        "author": ".author-name",
    },
)
```

**Parameters**:
- `html` (str): HTML content
- `selectors` (dict): CSS selectors for each field

**Returns**:
- `dict`: Extracted content with keys matching selectors

#### parse_with_readability(html: str) → dict

Parse HTML using Readability algorithm.

```python
from _src.parse import parse_with_readability

content = parse_with_readability(html)
```

**Parameters**:
- `html` (str): HTML content

**Returns**:
- `dict`: Extracted content with keys:
  - `title` (str): Article title
  - `body` (str): Main content
  - `author` (str, optional): Author name

#### extract_metadata(html: str) → dict

Extract metadata from HTML.

```python
from _src.parse import extract_metadata

metadata = extract_metadata(html)
```

**Parameters**:
- `html` (str): HTML content

**Returns**:
- `dict`: Metadata with keys:
  - `title` (str): og:title or title tag
  - `description` (str): og:description or meta description
  - `author` (str): og:author or article:author
  - `timestamp` (str): article:published_time

### _src.storage

Data storage and retrieval.

#### save_capture(html: str, url: str) → str

Save raw HTML capture.

```python
from _src.storage import save_capture

path = save_capture(
    html=html,
    url="https://example.com/article",
)
```

**Parameters**:
- `html` (str): HTML content
- `url` (str): Source URL

**Returns**:
- `str`: Path to saved file

#### save_feed(content: dict, url: str) → str

Save structured feed.

```python
from _src.storage import save_feed

path = save_feed(
    content={
        "title": "Article Title",
        "body": "Content...",
        "author": "Author Name",
    },
    url="https://example.com/article",
)
```

**Parameters**:
- `content` (dict): Structured content
- `url` (str): Source URL

**Returns**:
- `str`: Path to saved file

#### load_feed(path: str) → dict

Load structured feed.

```python
from _src.storage import load_feed

content = load_feed("data/feeds/20260316T103000Z_generic_html.json")
```

**Parameters**:
- `path` (str): Path to feed file

**Returns**:
- `dict`: Feed content

## Data Models

### BaseCrawler

Base class for all crawlers.

```python
from _src.base import BaseCrawler, WorkflowFetch, WorkflowParse

class MyCrawler(BaseCrawler):
    fetch = WorkflowFetch(...)
    parse = WorkflowParse(...)
```

**Attributes**:
- `fetch` (WorkflowFetch): Fetch configuration
- `parse` (WorkflowParse): Parse configuration

**Methods**:

##### async crawl(url: str) → dict

Crawl a URL and return structured content.

```python
crawler = MyCrawler()
content = await crawler.crawl("https://example.com")
```

### WorkflowFetch

Fetch configuration.

```python
from _src.base import WorkflowFetch, FetchMode

fetch = WorkflowFetch(
    mode=FetchMode.http,
    fallback=FetchMode.browser,
    timeout=30,
    headers={"User-Agent": "Tapestry/1.0"},
)
```

**Attributes**:
- `mode` (FetchMode): Primary fetch method
- `fallback` (FetchMode, optional): Fallback method
- `timeout` (int): Timeout in seconds
- `headers` (dict, optional): Custom headers

### WorkflowParse

Parse configuration.

```python
from _src.base import WorkflowParse

parse = WorkflowParse(
    title="h1, .title",
    body="article, main",
    author=".author-name",
    readability_fallback=True,
)
```

**Attributes**:
- `title` (str): CSS selector for title
- `body` (str): CSS selector for body
- `author` (str, optional): CSS selector for author
- `timestamp` (str, optional): CSS selector for timestamp
- `readability_fallback` (bool): Enable readability fallback
- `metadata_fallback` (bool): Enable metadata fallback

### FetchMode

Enum for fetch modes.

```python
from _src.base import FetchMode

FetchMode.http      # HTTP request
FetchMode.browser   # Browser rendering
```

## Knowledge Base API

### Catalog

#### read_catalog() → list

Read knowledge base catalog.

```python
from _src.kb import read_catalog

entries = read_catalog()
# Returns: List of catalog entries
```

**Returns**:
- `list[dict]`: Catalog entries with keys:
  - `path` (str): Note path
  - `title` (str): Note title
  - `topics` (list[str]): Topics
  - `timestamp` (str): ISO 8601 timestamp
  - `url` (str): Source URL

#### search_catalog(query: str) → list

Search catalog by query.

```python
from _src.kb import search_catalog

results = search_catalog("AI transformers")
```

**Parameters**:
- `query` (str): Search query

**Returns**:
- `list[dict]`: Matching catalog entries

#### add_catalog_entry(entry: dict)

Add entry to catalog.

```python
from _src.kb import add_catalog_entry

add_catalog_entry({
    "path": "ai-and-research/note.md",
    "title": "Article Title",
    "topics": ["AI", "research"],
    "timestamp": "2026-03-16T10:30:00Z",
    "url": "https://example.com",
})
```

**Parameters**:
- `entry` (dict): Catalog entry

### Notes

#### create_note(content: dict, chapter: str) → str

Create a knowledge base note.

```python
from _src.kb import create_note

path = create_note(
    content={
        "title": "Article Title",
        "body": "Content...",
        "url": "https://example.com",
    },
    chapter="ai-and-research/research-tracking",
)
```

**Parameters**:
- `content` (dict): Note content
- `chapter` (str): Chapter path

**Returns**:
- `str`: Path to created note

#### read_note(path: str) → str

Read a knowledge base note.

```python
from _src.kb import read_note

markdown = read_note("ai-and-research/note.md")
```

**Parameters**:
- `path` (str): Note path

**Returns**:
- `str`: Markdown content

## Utilities

### URL Utilities

```python
from _src.utils import normalize_url, extract_domain

# Normalize URL
url = normalize_url("https://example.com/page?utm_source=twitter")
# Returns: "https://example.com/page"

# Extract domain
domain = extract_domain("https://www.example.com/page")
# Returns: "example.com"
```

### Text Utilities

```python
from _src.utils import clean_text, truncate_text

# Clean text
text = clean_text("  Text with\n\nextra   spaces  ")
# Returns: "Text with extra spaces"

# Truncate text
text = truncate_text("Long text...", max_length=100)
# Returns: "Long text... (truncated)"
```

### Date Utilities

```python
from _src.utils import parse_timestamp, format_timestamp

# Parse timestamp
dt = parse_timestamp("2026-03-16T10:30:00Z")
# Returns: datetime object

# Format timestamp
iso = format_timestamp(dt)
# Returns: "2026-03-16T10:30:00Z"
```

## Error Handling

### Exceptions

```python
from _src.exceptions import (
    TapestryError,      # Base exception
    FetchError,         # Fetch failed
    ParseError,         # Parse failed
    StorageError,       # Storage failed
    CrawlerError,       # Crawler error
)

try:
    result = await service.ingest(url)
except FetchError as e:
    print(f"Fetch failed: {e}")
except ParseError as e:
    print(f"Parse failed: {e}")
except TapestryError as e:
    print(f"General error: {e}")
```

## Examples

### Basic Ingestion

```python
import asyncio
from _src.ingest import IngestionService

async def main():
    service = IngestionService()

    result = await service.ingest(
        url="https://example.com/article",
        context="Research on AI",
    )

    print(f"Saved to: {result['feed_path']}")
    print(f"Title: {result['content']['title']}")
    print(f"Body length: {len(result['content']['body'])}")

asyncio.run(main())
```

### Custom Crawler

```python
from _src.base import BaseCrawler, WorkflowFetch, WorkflowParse, FetchMode
from _src.registry import CrawlerRegistry

class MyPlatformCrawler(BaseCrawler):
    fetch = WorkflowFetch(mode=FetchMode.http)
    parse = WorkflowParse(
        title=".post-title",
        body=".post-content",
    )

# Register crawler
registry = CrawlerRegistry()
registry.register_crawler(
    name="myplatform",
    patterns=[r"myplatform\.com/.*"],
    crawler=MyPlatformCrawler,
)

# Use crawler
crawler = registry.get_crawler("https://myplatform.com/post/123")
content = await crawler.crawl("https://myplatform.com/post/123")
```

### Batch Processing

```python
import asyncio
from _src.ingest import IngestionService

async def main():
    service = IngestionService()

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]

    results = await service.ingest_batch(
        urls=urls,
        context="Research collection",
    )

    for result in results:
        print(f"Processed: {result['content']['title']}")

asyncio.run(main())
```

### Knowledge Base Search

```python
from _src.kb import search_catalog, read_note

# Search catalog
results = search_catalog("transformers")

# Read matching notes
for entry in results:
    note = read_note(entry["path"])
    print(f"Title: {entry['title']}")
    print(f"Path: {entry['path']}")
    print(f"Preview: {note[:200]}...")
```

## Type Hints

Tapestry uses type hints throughout:

```python
from typing import Optional, List, Dict, Any

async def ingest(
    url: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    ...

async def ingest_batch(
    urls: List[str],
    context: Optional[str] = None
) -> List[Dict[str, Any]]:
    ...
```

## Testing

### Unit Tests

```python
import pytest
from _src.parse import parse_with_selectors

def test_parse_with_selectors():
    html = "<h1>Title</h1><article>Content</article>"
    selectors = {"title": "h1", "body": "article"}

    result = parse_with_selectors(html, selectors)

    assert result["title"] == "Title"
    assert result["body"] == "Content"
```

### Async Tests

```python
import pytest
from _src.ingest import IngestionService

@pytest.mark.asyncio
async def test_ingest():
    service = IngestionService()

    result = await service.ingest("https://example.com")

    assert "content" in result
    assert result["content"]["title"]
```

## Best Practices

### Use Type Hints

```python
from typing import Dict, List

def process_content(content: Dict[str, str]) -> List[str]:
    return content["body"].split("\n")
```

### Handle Errors

```python
from _src.exceptions import FetchError, ParseError

try:
    result = await service.ingest(url)
except FetchError:
    # Retry with browser
    result = await service.ingest(url, force_browser=True)
except ParseError:
    # Log and skip
    logger.error(f"Failed to parse: {url}")
```

### Use Async/Await

```python
# Good: Concurrent processing
results = await asyncio.gather(
    service.ingest(url1),
    service.ingest(url2),
    service.ingest(url3),
)

# Bad: Sequential processing
results = []
for url in urls:
    result = await service.ingest(url)
    results.append(result)
```

## Next Steps

- Read [Architecture Overview](../architecture/overview.md)
- Explore [Crawler System](../architecture/crawlers.md)
- See [Configuration Reference](configuration.md)
