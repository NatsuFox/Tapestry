# Crawler System

Tapestry's crawler system provides unified content extraction across multiple platforms through a registry-based architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Crawler Registry                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  URL Pattern Matching                                │  │
│  │  - Regex patterns for each platform                  │  │
│  │  - Priority-based selection                          │  │
│  │  - Fallback to generic_html                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Zhihu   │    │ Reddit  │    │ Generic │
    │ Crawler │    │ Crawler │    │  HTML   │
    └─────────┘    └─────────┘    └─────────┘
```

## Crawler Interface

All crawlers implement a common interface:

```python
class BaseCrawler:
    """Base crawler interface"""

    # Configuration
    fetch: WorkflowFetch    # How to fetch content
    parse: WorkflowParse    # How to parse content

    # Methods
    async def fetch_content(url: str) -> str
    async def parse_content(html: str) -> dict
```

## Fetch Strategies

### HTTP Fetch (Default)
Fast, low-resource fetching for static content:

```python
fetch = WorkflowFetch(
    mode=FetchMode.http,
    fallback=FetchMode.browser,
)
```

**Pros**:
- Fast (< 1 second)
- Low resource usage
- Works for most sites

**Cons**:
- No JavaScript execution
- May miss dynamic content

### Browser Rendering (Fallback)
Full browser rendering for JavaScript-heavy sites:

```python
fetch = WorkflowFetch(
    mode=FetchMode.browser,
)
```

**Pros**:
- Full JavaScript execution
- Handles SPAs and dynamic content
- Accurate rendering

**Cons**:
- Slow (3-10 seconds)
- High resource usage
- Requires Playwright

## Parse Strategies

### CSS Selectors (Primary)
Fast, precise extraction using CSS selectors:

```python
parse = WorkflowParse(
    title="h1.title, .article-title",
    body="article.content, main",
    author=".author-name",
)
```

**Best for**:
- Well-structured HTML
- Known site layouts
- Consistent markup

### Readability (Fallback)
Content extraction using Mozilla's Readability algorithm:

```python
# Automatic fallback when CSS selectors fail
# No configuration needed
```

**Best for**:
- Unknown site layouts
- Varied HTML structures
- Article-like content

### Metadata Extraction (Last Resort)
Extract from Open Graph and meta tags:

```python
# Automatic fallback when other methods fail
# Extracts og:title, og:description, etc.
```

**Best for**:
- Minimal content extraction
- Fallback when nothing else works

## Platform-Specific Crawlers

### Zhihu Crawler
Handles Zhihu questions, answers, articles, and profiles:

**URL Patterns**:
- `zhihu.com/question/*/answer/*` - Answers
- `zhihu.com/question/*` - Questions
- `zhuanlan.zhihu.com/p/*` - Articles
- `zhihu.com/people/*` - Profiles

**Selectors**:
- Title: `.QuestionHeader-title`, `.Post-Title`
- Body: `.RichContent-inner`, `.Post-RichTextContainer`
- Author: `.AuthorInfo-name`
- Metadata: Vote counts, comment counts, timestamps

### Reddit Crawler
Handles Reddit threads and comments:

**URL Patterns**:
- `reddit.com/r/*/comments/*` - Threads

**Selectors**:
- Title: `[slot="title"]`
- Body: `[slot="text-body"]`
- Author: `[slot="authorName"]`
- Metadata: Upvotes, comment count

### Hacker News Crawler
Handles HN discussions:

**URL Patterns**:
- `news.ycombinator.com/item?id=*` - Discussions

**Selectors**:
- Title: `.titleline > a`
- Body: `.toptext`
- Comments: `.comment`
- Metadata: Points, comment count

### X/Twitter Crawler
Handles X (Twitter) posts:

**URL Patterns**:
- `x.com/*/status/*` - Posts
- `twitter.com/*/status/*` - Posts

**Fetch**: Browser rendering required (JavaScript-heavy)

### Xiaohongshu Crawler
Handles Xiaohongshu notes and profiles:

**URL Patterns**:
- `xiaohongshu.com/explore/*` - Notes
- `xiaohongshu.com/user/profile/*` - Profiles

**Fetch**: Browser rendering required

### Weibo Crawler
Handles Weibo posts:

**URL Patterns**:
- `weibo.com/*/[A-Z0-9]*` - Posts

**Fetch**: Browser rendering required

### Generic HTML Crawler
Fallback for any HTML page:

**URL Patterns**:
- `*` (matches everything)

**Selectors**:
- Title: `h1, .title, [class*='title']`
- Body: `article, main, .content, [role='main']`

**Fallback Chain**:
1. CSS selectors
2. Readability extraction
3. Browser rendering (if insufficient content)
4. Metadata extraction

## Content Quality Validation

All crawlers validate extracted content:

```python
if len(body) < 200:
    logger.warning(
        f"Extracted content is suspiciously short ({len(body)} chars) "
        f"for {url}. Consider using browser rendering."
    )
```

**Quality Indicators**:
- ✓ Body length > 500 characters
- ✓ Title extracted
- ✓ Structured content (paragraphs)
- ✗ Body length < 200 characters
- ✗ Only metadata description
- ✗ Missing title

## Adding New Crawlers

### 1. Create Crawler Class

```python
# _src/crawlers/myplatform/__init__.py

from ..base import BaseCrawler, WorkflowFetch, WorkflowParse, FetchMode

class MyPlatformCrawler(BaseCrawler):
    """Crawler for MyPlatform"""

    fetch = WorkflowFetch(
        mode=FetchMode.http,
        fallback=FetchMode.browser,
    )

    parse = WorkflowParse(
        title=".post-title",
        body=".post-content",
        author=".author-name",
    )
```

### 2. Register in Registry

```python
# _src/registry.py

from .crawlers.myplatform import MyPlatformCrawler

CRAWLER_REGISTRY = {
    "myplatform": {
        "patterns": [r"myplatform\.com/posts/.*"],
        "crawler": MyPlatformCrawler,
    },
    # ... other crawlers
}
```

### 3. Add Feed Schema

```python
# feed/_specs/myplatform_post.md

## MyPlatform Post Schema

- title: string
- body: string
- author: string
- timestamp: ISO 8601
- url: string
- metadata:
  - likes: integer
  - shares: integer
```

### 4. Test

```bash
python3 ingest/_scripts/run.py "https://myplatform.com/posts/123"
```

## Best Practices

### Selector Design
- Use multiple fallback selectors: `"h1, .title, [class*='title']"`
- Prefer semantic HTML: `article, main, [role='main']`
- Test with multiple pages from the platform

### Fetch Strategy
- Start with HTTP, fallback to browser
- Only use browser rendering when necessary
- Add delays for rate limiting

### Error Handling
- Graceful degradation when dependencies missing
- Clear error messages
- Log warnings for quality issues

### Testing
- Test with real URLs from the platform
- Verify content quality (length, structure)
- Check metadata extraction

## Performance Optimization

### Caching
- Cache fetched HTML to avoid redundant requests
- Store parsed results for reprocessing

### Parallel Processing
- Fetch multiple URLs concurrently
- Use async/await for I/O operations

### Resource Management
- Reuse browser instances
- Close connections properly
- Limit concurrent browser sessions

## Troubleshooting

### Short Content Extracted
**Symptom**: Body length < 200 characters

**Solutions**:
1. Enable browser rendering
2. Check CSS selectors
3. Verify readability is installed
4. Inspect raw HTML

### Import Errors
**Symptom**: `ModuleNotFoundError`

**Solutions**:
1. Verify dependencies installed
2. Check working directory
3. Install missing packages

### Browser Not Working
**Symptom**: Playwright errors

**Solutions**:
1. Install browser binaries: `playwright install chromium`
2. Check system dependencies (Linux)
3. Verify Playwright version

See [Troubleshooting Guide](../reference/troubleshooting.md) for more details.
