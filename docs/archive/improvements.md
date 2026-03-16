# Tapestry Content Extraction Improvements

## Problem Identified

The Tapestry system was producing superficial content in the knowledge base because:

1. **Missing CSS selectors**: The generic_html crawler had no CSS selectors configured
2. **Broken readability fallback**: Missing `chardet` dependency prevented the readability library from working
3. **No browser rendering**: JavaScript-heavy sites (like Mintlify docs) weren't being rendered
4. **No quality validation**: No warnings when content extraction failed

## Improvements Implemented

### 1. Fixed Readability Dependency ✓

**Issue**: The readability library requires `chardet` for encoding detection, but it wasn't installed.

**Solution**: Installed `chardet` package.

```bash
pip install chardet
```

**Impact**: Readability fallback now works for extracting main content from complex HTML.

### 2. Added Browser Rendering Fallback ✓

**Issue**: Modern JavaScript-rendered sites (like agentskills.io) have minimal server-side HTML.

**Solution**: Configured generic_html crawler to use browser rendering as fallback.

**Changes**:
- Added `FetchMode.browser` as fallback in `WorkflowFetch`
- Browser rendering automatically triggers when HTTP fetch produces insufficient content
- Uses Playwright with Chromium for JavaScript execution

**Configuration**:
```python
fetch=WorkflowFetch(
    mode=FetchMode.http,
    fallback=FetchMode.browser,
)
```

### 3. Enhanced CSS Selectors ✓

**Issue**: Generic HTML crawler had empty `WorkflowParse()` with no selectors.

**Solution**: Added intelligent CSS selectors for common content patterns.

**Selectors added**:
- **Title**: `h1, .title, [class*='title'], [id*='title']`
- **Body**: `article, main, .content, [role='main'], .main-content, #content`

**Parser enhancement**: Modified `_select_text()` to try multiple comma-separated selectors in order.

### 4. Added Content Quality Validation ✓

**Issue**: No warnings when content extraction produced suspiciously short results.

**Solution**: Added logging warning when extracted content is < 200 characters.

**Warning message**:
```
Extracted content is suspiciously short (70 chars) for https://example.com.
Consider using browser rendering for JavaScript-heavy sites.
```

## Results

### Before
- **Body length**: 70 characters (just metadata description)
- **Content**: "A simple, open format for giving agents new capabilities and expertise."
- **Fetch mode**: HTTP only

### After
- **Body length**: 1,878 characters (full article content)
- **Content**: Complete overview including "Why Agent Skills?", "What can Agent Skills enable?", adoption info, etc.
- **Fetch mode**: HTTP with browser fallback

## Testing

Verified improvements by re-ingesting https://agentskills.io/home:

```bash
python3 ingest/_scripts/run.py "https://agentskills.io/home"
```

**Results**:
- ✓ Content extraction successful
- ✓ 1,878 characters extracted (26x improvement)
- ✓ Browser fallback working
- ✓ CSS selectors working
- ✓ Readability fallback available
- ✓ No import errors

## Architecture

The extraction pipeline now follows this fallback chain:

1. **HTTP Fetch** → Try CSS selectors
2. If content insufficient → **Readability extraction**
3. If still insufficient → **Browser rendering** (Playwright)
4. If still insufficient → **Metadata extraction** (og:description)

## Dependencies

All dependencies are now documented in a single requirements.txt file:

### Installation

```bash
# Install all dependencies (includes browser support)
pip install -r requirements.txt
playwright install chromium

# Or install with pyproject.toml
pip install -e ".[browser]"
```

See [installation.md](installation.md) for detailed installation instructions.

### Required Packages

- `httpx>=0.27.0` - Async HTTP client
- `pydantic>=2.0.0` - Data validation
- `selectolax>=0.3.0` - Fast HTML parsing
- `readability-lxml>=0.8.0` - Content extraction
- `chardet>=5.0.0` - Encoding detection

### Recommended Packages

- `playwright>=1.40.0` - Browser rendering (included by default)

## Future Enhancements

Potential improvements for even better content extraction:

1. **LLM-based extraction**: Use Claude to extract structured content from HTML
2. **Site-specific crawlers**: Add dedicated crawlers for common documentation sites
3. **Content scoring**: Implement quality metrics to automatically choose best extraction method
4. **Caching**: Cache browser-rendered pages to avoid repeated rendering
5. **Parallel extraction**: Try multiple methods in parallel and choose best result

## Files Modified

1. `_src/crawlers/generic_html/__init__.py` - Added fetch config and CSS selectors
2. `_src/parse.py` - Enhanced selector logic and added quality validation

## Compatibility

All changes are backward compatible:
- Existing crawlers continue to work
- HTTP-only mode still available
- Browser rendering is optional (graceful degradation if Playwright not installed)
