# Content Pipeline

The Tapestry content pipeline transforms raw URLs into organized knowledge through a series of well-defined stages.

## Pipeline Overview

```
┌──────────┐
│   URL    │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 1: URL ROUTING                                    │
│ - Pattern matching                                      │
│ - Crawler selection                                     │
│ - Validation                                            │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 2: FETCH                                          │
│ ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│ │  HTTP   │ -> │ Browser │ -> │  Store  │            │
│ │ Request │    │ Render  │    │  HTML   │            │
│ └─────────┘    └─────────┘    └─────────┘            │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 3: PARSE                                          │
│ ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│ │   CSS   │ -> │ Readab. │ -> │ Metadata│            │
│ │Selectors│    │ Extract │    │ Extract │            │
│ └─────────┘    └─────────┘    └─────────┘            │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 4: VALIDATE                                       │
│ - Content quality check                                 │
│ - Length validation                                     │
│ - Structure verification                                │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 5: NORMALIZE                                      │
│ - Platform-specific → Standard schema                   │
│ - Metadata enrichment                                   │
│ - Timestamp normalization                               │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 6: STORE                                          │
│ ┌─────────┐    ┌─────────┐                            │
│ │ Capture │    │  Feed   │                            │
│ │  (HTML) │    │ (JSON)  │                            │
│ └─────────┘    └─────────┘                            │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 7: SYNTHESIZE (Optional)                          │
│ - AI analysis                                           │
│ - Topic extraction                                      │
│ - Knowledge base organization                           │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────┐
│ Knowledge    │
│ Base Note    │
└──────────────┘
```

## Stage Details

### Stage 1: URL Routing

**Purpose**: Determine which crawler to use

**Process**:
1. Extract domain and path from URL
2. Match against registered crawler patterns
3. Select highest-priority matching crawler
4. Fallback to generic_html if no match

**Example**:
```python
url = "https://www.zhihu.com/question/123/answer/456"
# Matches pattern: r"zhihu\.com/question/.*/answer/.*"
# Selects: ZhihuAnswerCrawler
```

**Output**: Crawler instance

### Stage 2: Fetch

**Purpose**: Retrieve HTML content

**Fetch Modes**:

#### HTTP Fetch (Primary)
```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    html = response.text
```

**Characteristics**:
- Fast (< 1 second)
- Low resource usage
- No JavaScript execution

#### Browser Rendering (Fallback)
```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(url)
    html = await page.content()
```

**Characteristics**:
- Slow (3-10 seconds)
- High resource usage
- Full JavaScript execution

**Fallback Logic**:
```python
if fetch_mode == FetchMode.http:
    html = await http_fetch(url)
    if is_insufficient(html):
        html = await browser_fetch(url)
```

**Output**: Raw HTML string

### Stage 3: Parse

**Purpose**: Extract structured content from HTML

**Parse Methods**:

#### CSS Selectors (Primary)
```python
from selectolax.parser import HTMLParser

tree = HTMLParser(html)
title = tree.css_first("h1.title").text()
body = tree.css_first("article.content").text()
```

**Characteristics**:
- Fast (< 100ms)
- Precise
- Requires known selectors

#### Readability (Fallback)
```python
from readability import Document

doc = Document(html)
title = doc.title()
body = doc.summary()
```

**Characteristics**:
- Moderate speed (< 500ms)
- Heuristic-based
- Works on unknown layouts

#### Metadata Extraction (Last Resort)
```python
og_title = tree.css_first('meta[property="og:title"]')
og_description = tree.css_first('meta[property="og:description"]')
```

**Characteristics**:
- Fast (< 50ms)
- Limited content
- Always available

**Fallback Chain**:
```python
# Try CSS selectors
content = extract_with_selectors(html)

if not content or len(content) < 200:
    # Try readability
    content = extract_with_readability(html)

if not content or len(content) < 100:
    # Try metadata
    content = extract_metadata(html)
```

**Output**: Structured dict with title, body, author, etc.

### Stage 4: Validate

**Purpose**: Ensure content quality

**Validation Checks**:

```python
def validate_content(content: dict) -> bool:
    # Check title
    if not content.get("title"):
        logger.warning("Missing title")

    # Check body length
    body = content.get("body", "")
    if len(body) < 200:
        logger.warning(
            f"Suspiciously short content ({len(body)} chars). "
            "Consider browser rendering."
        )

    # Check structure
    if not has_paragraphs(body):
        logger.warning("Content lacks structure")

    return True  # Continue even with warnings
```

**Quality Indicators**:
- ✓ Title present
- ✓ Body > 500 characters
- ✓ Structured content (paragraphs, sections)
- ✓ Author information
- ✓ Timestamp

**Output**: Validated content dict + warnings

### Stage 5: Normalize

**Purpose**: Transform to standard schema

**Normalization Process**:

```python
# Platform-specific format
zhihu_answer = {
    "question_title": "...",
    "answer_content": "...",
    "author_name": "...",
    "voteup_count": 123,
}

# Normalized format
normalized = {
    "title": zhihu_answer["question_title"],
    "body": zhihu_answer["answer_content"],
    "author": zhihu_answer["author_name"],
    "metadata": {
        "votes": zhihu_answer["voteup_count"],
    },
    "platform": "zhihu",
    "content_type": "answer",
    "url": original_url,
    "timestamp": iso8601_timestamp,
}
```

**Standard Schema**:
```python
{
    "title": str,           # Required
    "body": str,            # Required
    "author": str,          # Optional
    "timestamp": str,       # ISO 8601
    "url": str,             # Original URL
    "platform": str,        # Source platform
    "content_type": str,    # Type of content
    "metadata": dict,       # Platform-specific data
}
```

**Output**: Normalized JSON

### Stage 6: Store

**Purpose**: Persist data for future use

**Storage Locations**:

#### Captures (Raw HTML)
```
data/captures/
└── 20260316T103000Z_zhihu_answer_123456.html
```

**Format**: Raw HTML
**Purpose**: Reproducibility, reprocessing

#### Feeds (Structured JSON)
```
data/feeds/
└── 20260316T103000Z_zhihu_answer_123456.json
```

**Format**: Normalized JSON
**Purpose**: Structured access, analysis

**File Naming**:
```python
timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
platform = "zhihu"
content_type = "answer"
content_id = "123456"

filename = f"{timestamp}_{platform}_{content_type}_{content_id}"
```

**Output**: File paths

### Stage 7: Synthesize (Optional)

**Purpose**: Organize into knowledge base

**Synthesis Process**:

```python
# 1. Analyze content
analysis = await ai_analyze(content)
topics = analysis["topics"]
themes = analysis["themes"]

# 2. Determine placement
chapter = determine_chapter(topics, themes)
filename = generate_filename(content)

# 3. Create note
note = create_markdown_note(content, analysis)

# 4. Update catalog
catalog.add_entry(
    path=f"knowledge-base/{chapter}/{filename}",
    topics=topics,
    timestamp=content["timestamp"],
)
```

**Knowledge Base Structure**:
```
knowledge-base/
├── ai-and-research/
│   ├── index.md
│   └── research-tracking/
│       └── 20260316T103000Z-overview.md
├── community-qa/
│   └── ...
└── catalog.jsonl
```

**Output**: Markdown note + catalog entry

## Data Flow Example

### Input
```
URL: https://www.zhihu.com/question/123/answer/456
Context: "Research on AI agents"
```

### Stage 1: Routing
```python
crawler = ZhihuAnswerCrawler
```

### Stage 2: Fetch
```python
html = await http_fetch(url)
# 15KB HTML content
```

### Stage 3: Parse
```python
content = {
    "title": "How do AI agents work?",
    "body": "AI agents are...",  # 2,500 chars
    "author": "张三",
    "votes": 123,
}
```

### Stage 4: Validate
```python
# ✓ Title present
# ✓ Body length: 2,500 chars
# ✓ Author present
# No warnings
```

### Stage 5: Normalize
```python
normalized = {
    "title": "How do AI agents work?",
    "body": "AI agents are...",
    "author": "张三",
    "timestamp": "2026-03-16T10:30:00Z",
    "url": "https://www.zhihu.com/question/123/answer/456",
    "platform": "zhihu",
    "content_type": "answer",
    "metadata": {"votes": 123},
}
```

### Stage 6: Store
```python
# Capture
data/captures/20260316T103000Z_zhihu_answer_456.html

# Feed
data/feeds/20260316T103000Z_zhihu_answer_456.json
```

### Stage 7: Synthesize
```python
# Analysis
topics = ["AI", "agents", "research"]
chapter = "ai-and-research"

# Note
knowledge-base/ai-and-research/20260316T103000Z-how-ai-agents-work.md

# Catalog entry
{"path": "...", "topics": [...], "timestamp": "..."}
```

## Pipeline Configuration

### Fetch Configuration
```python
fetch = WorkflowFetch(
    mode=FetchMode.http,        # Primary method
    fallback=FetchMode.browser,  # Fallback method
    timeout=30,                  # Request timeout
    headers={...},               # Custom headers
)
```

### Parse Configuration
```python
parse = WorkflowParse(
    title="h1, .title",          # Title selectors
    body="article, main",        # Body selectors
    author=".author-name",       # Author selectors
    readability_fallback=True,   # Enable fallback
)
```

### Validation Configuration
```python
validation = ValidationConfig(
    min_body_length=200,         # Minimum body length
    require_title=True,          # Title required
    warn_on_short=True,          # Warn if short
)
```

## Error Handling

### Fetch Errors
```python
try:
    html = await fetch(url)
except httpx.HTTPError as e:
    # Try browser fallback
    html = await browser_fetch(url)
except Exception as e:
    logger.error(f"Fetch failed: {e}")
    raise
```

### Parse Errors
```python
try:
    content = parse_with_selectors(html)
except Exception as e:
    # Try readability fallback
    content = parse_with_readability(html)
```

### Storage Errors
```python
try:
    save_capture(html, path)
except IOError as e:
    logger.error(f"Failed to save capture: {e}")
    # Continue with feed storage
```

## Performance Optimization

### Caching
- Cache fetched HTML
- Reuse parsed results
- Store intermediate data

### Parallel Processing
- Fetch multiple URLs concurrently
- Parse in parallel
- Batch storage operations

### Resource Management
- Reuse HTTP clients
- Pool browser instances
- Limit concurrent operations

## Monitoring

### Metrics
- Fetch success rate
- Parse success rate
- Average content length
- Processing time per stage

### Logging
```python
logger.info(f"Fetched {url} in {elapsed}s")
logger.warning(f"Short content: {len(body)} chars")
logger.error(f"Parse failed: {error}")
```

See [Troubleshooting Guide](../reference/troubleshooting.md) for common issues.
