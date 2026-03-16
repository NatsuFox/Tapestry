# Basic Usage

This guide covers the fundamental operations for using Tapestry to capture and organize web content.

## Prerequisites

Before starting, ensure you have:
- Installed Tapestry (see [Installation Guide](../installation.md))
- Verified dependencies are working
- Basic familiarity with command line

## Quick Start

### Single URL Ingestion

The simplest way to use Tapestry:

```bash
cd skills/tapestry
python3 ingest/_scripts/run.py "https://example.com/article"
```

**What happens**:
1. URL is fetched (HTTP or browser)
2. Content is extracted (CSS selectors or readability)
3. Raw HTML is saved to `data/captures/`
4. Structured JSON is saved to `data/feeds/`

**Output**:
```
✓ Fetched https://example.com/article
✓ Extracted 1,234 characters
✓ Saved capture: data/captures/20260316T103000Z_generic_html.html
✓ Saved feed: data/feeds/20260316T103000Z_generic_html.json
```

### Multiple URLs

Process multiple URLs in one command:

```bash
python3 ingest/_scripts/run.py \
  "https://example.com/page1" \
  "https://example.com/page2" \
  "https://example.com/page3"
```

**Benefits**:
- Faster than running separately
- Shared HTTP client
- Batch processing

### With Context

Add context to help with organization:

```bash
python3 ingest/_scripts/run.py \
  --text "Research on AI agents and LLMs" \
  "https://example.com/article"
```

**Context uses**:
- Helps AI understand your intent
- Improves knowledge base organization
- Provides additional metadata

## Supported Platforms

Tapestry automatically detects and handles these platforms:

### Zhihu
```bash
# Question
python3 ingest/_scripts/run.py "https://www.zhihu.com/question/123456"

# Answer
python3 ingest/_scripts/run.py "https://www.zhihu.com/question/123/answer/456"

# Article
python3 ingest/_scripts/run.py "https://zhuanlan.zhihu.com/p/123456"

# Profile
python3 ingest/_scripts/run.py "https://www.zhihu.com/people/username"
```

### Reddit
```bash
# Thread
python3 ingest/_scripts/run.py "https://www.reddit.com/r/programming/comments/abc123/title/"
```

### Hacker News
```bash
# Discussion
python3 ingest/_scripts/run.py "https://news.ycombinator.com/item?id=123456"
```

### X (Twitter)
```bash
# Post
python3 ingest/_scripts/run.py "https://x.com/username/status/123456"
```

### Xiaohongshu
```bash
# Note
python3 ingest/_scripts/run.py "https://www.xiaohongshu.com/explore/123456"

# Profile
python3 ingest/_scripts/run.py "https://www.xiaohongshu.com/user/profile/123456"
```

### Weibo
```bash
# Post
python3 ingest/_scripts/run.py "https://weibo.com/123456/ABC123"
```

### Generic HTML
```bash
# Any webpage
python3 ingest/_scripts/run.py "https://blog.example.com/post"
```

## Understanding Output

### Captures (Raw HTML)

Location: `data/captures/`

**Purpose**: Preserve original HTML for reproducibility

**Format**:
```
20260316T103000Z_zhihu_answer_123456.html
```

**When to use**:
- Reprocess with different settings
- Debug extraction issues
- Archive original content

### Feeds (Structured JSON)

Location: `data/feeds/`

**Purpose**: Normalized, structured data

**Format**:
```json
{
  "title": "Article Title",
  "body": "Full article content...",
  "author": "Author Name",
  "timestamp": "2026-03-16T10:30:00Z",
  "url": "https://example.com/article",
  "platform": "generic_html",
  "content_type": "article",
  "metadata": {}
}
```

**When to use**:
- Programmatic access
- Data analysis
- Export to other tools

## Common Workflows

### Research Collection

Collect articles on a specific topic:

```bash
python3 ingest/_scripts/run.py \
  --text "Machine learning optimization techniques" \
  "https://arxiv.org/abs/2301.12345" \
  "https://blog.example.com/ml-optimization" \
  "https://www.reddit.com/r/MachineLearning/comments/abc123/"
```

### Discussion Archival

Archive a discussion thread:

```bash
python3 ingest/_scripts/run.py \
  "https://news.ycombinator.com/item?id=123456"
```

### Profile Backup

Backup a user's profile:

```bash
python3 ingest/_scripts/run.py \
  "https://www.zhihu.com/people/username"
```

### Documentation Capture

Capture documentation pages:

```bash
python3 ingest/_scripts/run.py \
  "https://docs.example.com/getting-started" \
  "https://docs.example.com/api-reference" \
  "https://docs.example.com/examples"
```

## Quality Indicators

### Good Extraction

Signs of successful extraction:

```
✓ Extracted 2,345 characters
✓ Title: "Complete Article Title"
✓ Author: "Author Name"
✓ Structured content with paragraphs
```

**Characteristics**:
- Body length > 500 characters
- Title present
- Author information
- No warnings

### Poor Extraction

Signs of failed extraction:

```
⚠ Extracted content is suspiciously short (70 chars)
⚠ Missing title
⚠ Only metadata description
```

**Characteristics**:
- Body length < 200 characters
- Missing title
- Only og:description
- Warning messages

**Solutions**:
1. Enable browser rendering (install Playwright)
2. Check if site requires JavaScript
3. Verify CSS selectors
4. Try different URL format

## Troubleshooting

### Short Content

**Problem**: Extracted content is too short

**Diagnosis**:
```bash
# Check if browser rendering is available
python3 -c "from playwright.async_api import async_playwright; print('OK')"
```

**Solutions**:
1. Install browser support:
   ```bash
   pip install -r requirements-browser.txt
   playwright install chromium
   ```
2. Verify the site isn't blocking requests
3. Check if content is behind login

### Import Errors

**Problem**: `ModuleNotFoundError`

**Diagnosis**:
```bash
# Check dependencies
pip list | grep -E "httpx|pydantic|selectolax|readability|chardet"
```

**Solutions**:
1. Install missing dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Verify working directory:
   ```bash
   cd skills/tapestry
   ```

### Browser Not Working

**Problem**: Playwright errors

**Diagnosis**:
```bash
# Test browser
python3 -c "from playwright.async_api import async_playwright; print('OK')"
```

**Solutions**:
1. Install browser binaries:
   ```bash
   playwright install chromium
   ```
2. Check system dependencies (Linux):
   ```bash
   sudo apt-get install -y libnss3 libnspr4 libatk1.0-0
   ```

See [Troubleshooting Guide](../reference/troubleshooting.md) for more details.

## Next Steps

- Learn about [Knowledge Base](knowledge-base.md) organization
- Explore [Advanced Workflows](advanced-workflows.md)
- Read [Architecture Overview](../architecture/overview.md)
