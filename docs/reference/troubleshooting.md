# Troubleshooting Guide

Common issues and solutions for Tapestry.

## Installation Issues

### Missing Dependencies

**Symptom**:
```
ModuleNotFoundError: No module named 'httpx'
ModuleNotFoundError: No module named 'selectolax'
```

**Solution**:
```bash
# Install core dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "httpx|pydantic|selectolax|readability|chardet"
```

### Chardet Not Found

**Symptom**:
```
ModuleNotFoundError: No module named 'chardet'
```

**Solution**:
```bash
pip install chardet
```

**Why**: Readability library requires chardet for encoding detection.

### Playwright Not Installed

**Symptom**:
```
ModuleNotFoundError: No module named 'playwright'
```

**Solution**:
```bash
# Install playwright
pip install -r requirements-browser.txt

# Install browser binaries
playwright install chromium
```

### Browser Binaries Missing

**Symptom**:
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**Solution**:
```bash
playwright install chromium
```

### Linux System Dependencies

**Symptom**:
```
Error: Failed to launch browser
```

**Solution** (Debian/Ubuntu):
```bash
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

## Content Extraction Issues

### Short Content Extracted

**Symptom**:
```
⚠ Extracted content is suspiciously short (70 chars)
```

**Diagnosis**:
```bash
# Check if browser rendering is available
python3 -c "from playwright.async_api import async_playwright; print('OK')"
```

**Solutions**:

1. **Install browser support**:
   ```bash
   pip install -r requirements-browser.txt
   playwright install chromium
   ```

2. **Check if site requires JavaScript**:
   - View page source in browser
   - If content is minimal, site needs browser rendering

3. **Verify CSS selectors**:
   - Inspect HTML structure
   - Check if selectors match actual elements

4. **Try different URL format**:
   - Some sites have mobile vs desktop URLs
   - Try alternative URL patterns

### Missing Title

**Symptom**:
```
⚠ Missing title
```

**Solutions**:

1. **Check HTML structure**:
   ```bash
   # View raw HTML
   curl -s "https://example.com" | grep -i "<title>"
   ```

2. **Verify selectors**:
   - Inspect page in browser
   - Check if title is in expected location

3. **Enable browser rendering**:
   - Title might be JavaScript-rendered

### Only Metadata Extracted

**Symptom**:
Content is just og:description (< 200 chars)

**Cause**: All extraction methods failed

**Solutions**:

1. **Enable browser rendering**:
   ```bash
   pip install -r requirements-browser.txt
   playwright install chromium
   ```

2. **Check if content is behind login**:
   - Some sites require authentication
   - Tapestry doesn't handle login

3. **Verify URL is correct**:
   - Check for typos
   - Ensure URL is publicly accessible

### Content Lacks Structure

**Symptom**:
Content is one long string without paragraphs

**Solutions**:

1. **Check HTML structure**:
   - Inspect page source
   - Verify content has proper HTML tags

2. **Try readability fallback**:
   - Should automatically activate
   - Verify chardet is installed

3. **Use browser rendering**:
   - May improve structure extraction

## Runtime Issues

### Import Errors

**Symptom**:
```
ImportError: cannot import name 'CrawlerRegistry'
```

**Solution**:
```bash
# Verify working directory
cd skills/tapestry

# Test import
python3 -c "from _src.registry import CrawlerRegistry; print('OK')"
```

### HTTP Errors

**Symptom**:
```
httpx.HTTPError: 404 Not Found
httpx.HTTPError: 403 Forbidden
```

**Solutions**:

1. **404 Not Found**:
   - Verify URL is correct
   - Check if content still exists

2. **403 Forbidden**:
   - Site may be blocking requests
   - Try browser rendering
   - Check if site requires authentication

3. **Timeout**:
   - Increase timeout in configuration
   - Check network connection

### Browser Errors

**Symptom**:
```
playwright._impl._api_types.Error: Timeout 30000ms exceeded
```

**Solutions**:

1. **Increase timeout**:
   ```python
   # In crawler configuration
   fetch = WorkflowFetch(
       mode=FetchMode.browser,
       timeout=60,  # Increase to 60 seconds
   )
   ```

2. **Check network connection**:
   - Verify internet access
   - Check if site is accessible

3. **Try different browser**:
   ```bash
   # Install Firefox instead
   playwright install firefox
   ```

### Memory Issues

**Symptom**:
```
MemoryError
```

**Solutions**:

1. **Process URLs in smaller batches**:
   ```bash
   # Instead of 100 URLs at once
   # Process 10 at a time
   ```

2. **Close browser instances**:
   - Ensure proper cleanup
   - Limit concurrent browser sessions

3. **Increase system memory**:
   - Close other applications
   - Use swap space

## Data Issues

### Duplicate Content

**Symptom**:
Same content saved multiple times

**Solution**:
Tapestry automatically detects duplicates by URL. If you're seeing duplicates:

1. **Check if URLs are different**:
   - `example.com/page` vs `example.com/page/`
   - Query parameters: `?utm_source=...`

2. **Manual deduplication**:
   ```bash
   # Find duplicates in feeds
   cd data/feeds
   ls -1 | sort | uniq -d
   ```

### Corrupted Captures

**Symptom**:
HTML files are empty or corrupted

**Solutions**:

1. **Check disk space**:
   ```bash
   df -h
   ```

2. **Verify file permissions**:
   ```bash
   ls -la data/captures/
   ```

3. **Re-fetch content**:
   ```bash
   # Delete corrupted file
   rm data/captures/corrupted_file.html

   # Re-run ingestion
   python3 ingest/_scripts/run.py "URL"
   ```

### Invalid JSON

**Symptom**:
```
json.JSONDecodeError: Expecting value
```

**Solutions**:

1. **Check file encoding**:
   ```bash
   file data/feeds/file.json
   ```

2. **Validate JSON**:
   ```bash
   python3 -m json.tool data/feeds/file.json
   ```

3. **Re-generate feed**:
   - Delete invalid JSON
   - Re-run ingestion

## Performance Issues

### Slow Fetching

**Symptom**:
Fetching takes > 30 seconds per URL

**Solutions**:

1. **Check if browser rendering is being used**:
   - Browser rendering is slow (3-10s per URL)
   - Use HTTP mode when possible

2. **Optimize browser usage**:
   - Reuse browser instances
   - Limit concurrent sessions

3. **Check network speed**:
   ```bash
   # Test download speed
   curl -o /dev/null https://example.com
   ```

### High Memory Usage

**Symptom**:
Process uses > 1GB memory

**Solutions**:

1. **Limit concurrent operations**:
   - Process fewer URLs at once
   - Close browser instances

2. **Use HTTP mode**:
   - Avoid browser rendering when possible
   - HTTP mode uses much less memory

3. **Monitor resource usage**:
   ```bash
   # Check memory usage
   ps aux | grep python
   ```

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Inspect Raw HTML

```bash
# View captured HTML
cat data/captures/20260316T103000Z_*.html | less
```

### Test Selectors

```python
from selectolax.parser import HTMLParser

html = open("data/captures/file.html").read()
tree = HTMLParser(html)

# Test selector
title = tree.css_first("h1")
print(title.text() if title else "Not found")
```

### Test Readability

```python
from readability import Document

html = open("data/captures/file.html").read()
doc = Document(html)

print("Title:", doc.title())
print("Body:", doc.summary()[:200])
```

### Test Browser Rendering

```python
from playwright.async_api import async_playwright
import asyncio

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        content = await page.content()
        print(content[:500])
        await browser.close()

asyncio.run(test())
```

## Getting Help

### Check Documentation

- [Installation Guide](../installation.md)
- [Basic Usage](../guides/basic-usage.md)
- [Architecture Overview](../architecture/overview.md)

### Search Issues

Check if your issue has been reported:
- GitHub Issues: https://github.com/NatsuFox/Tapestry/issues

### Report a Bug

If you've found a bug:

1. **Gather information**:
   - Python version: `python3 --version`
   - Dependencies: `pip list`
   - Error message
   - URL that failed

2. **Create minimal reproduction**:
   ```bash
   python3 ingest/_scripts/run.py "URL_THAT_FAILS"
   ```

3. **Open an issue**:
   - Include error message
   - Include reproduction steps
   - Include system information

### Ask for Help

- GitHub Discussions: https://github.com/NatsuFox/Tapestry/discussions
- Include relevant details from debugging steps above

## Common Error Messages

### `ModuleNotFoundError`
→ See [Missing Dependencies](#missing-dependencies)

### `Executable doesn't exist`
→ See [Browser Binaries Missing](#browser-binaries-missing)

### `Suspiciously short content`
→ See [Short Content Extracted](#short-content-extracted)

### `HTTPError: 403 Forbidden`
→ See [HTTP Errors](#http-errors)

### `Timeout exceeded`
→ See [Browser Errors](#browser-errors)

### `MemoryError`
→ See [Memory Issues](#memory-issues)

### Viewer shows only one topic
→ See [Viewer Shows Only One Topic](#viewer-shows-only-one-topic-instead-of-all-knowledge-bases)

### Ingested data missing from viewer
→ See [Data Written to Wrong Directory](#data-written-to-wrong-directory)

---

## Display / Viewer Issues

### Viewer Shows Only One Topic Instead of All Knowledge Bases

**Symptom**: The viewer loads but displays only one KB topic (e.g., `dingyi-dex-weekly`) even though multiple topics exist under `_data/books/`.

**Root cause**: Either:
- `publish_viewer.py` was called with `--data-path _data/books/<topic>`, scoping the build to one topic.
- The HTTP server was started from a topic-specific `_viewer/` instead of `_data/books/_viewer`.

**Solution**:
```bash
# 1. Rebuild the full KB viewer (omit --data-path entirely)
python skills/tapestry/display/_scripts/publish_viewer.py --force

# 2. Kill any old server
fuser -k <port>/tcp   # or: kill <PID>

# 3. Serve from the FULL books/_viewer
python -m http.server <port> --directory <skill_root>/_data/books/_viewer
```

**Rule**: `--data-path` scopes the viewer to that path only. Omit it to show all topics.

---

### Data Written to Wrong Directory

**Symptom**: After ingestion/synthesis, notes and books appear under a path like `/root/.agents/_data/` but the viewer (which reads from `<config data_dir>`) shows nothing.

**Root cause**: The skill's working directory at invocation time differed from `config.data_dir`. Files were written relative to CWD instead of the canonical `data_dir`.

**Diagnosis**:
```bash
# Check what data_dir is configured
cat <skill_root>/config/tapestry.config.json | grep data_dir

# Check where notes actually landed
ls <wrong_path>/notes/
ls <correct_data_dir>/notes/
```

**Solution** (merge wrong → correct path):
```bash
# Merge notes, captures, feeds, books
cp -rn <wrong_data_dir>/notes/  <correct_data_dir>/notes/
cp -rn <wrong_data_dir>/captures/ <correct_data_dir>/captures/
cp -rn <wrong_data_dir>/feeds/   <correct_data_dir>/feeds/
cp -rn <wrong_data_dir>/books/   <correct_data_dir>/books/

# Merge catalog entries (avoid duplicates)
cat <wrong_data_dir>/catalog.jsonl >> <correct_data_dir>/catalog.jsonl
sort -u <correct_data_dir>/catalog.jsonl -o <correct_data_dir>/catalog.jsonl
```

**Prevention**: Before running ingest/synthesis, verify `config.data_dir` matches the intended path:
```bash
python3 -c "from tapestry._src.config import TapestryConfig; c = TapestryConfig.load(); print(c.data_dir)"
```
