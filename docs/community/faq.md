# Frequently Asked Questions (FAQ)

Common questions about Tapestry and their answers.

## General Questions

### What is Tapestry?

Tapestry is an AI-native skill package for capturing, organizing, and synthesizing web content from multiple platforms. It's designed to work with agent frameworks like Claude Code, transforming scattered web content into a structured, searchable knowledge base.

### Is Tapestry a library or a tool?

Neither exactly. Tapestry is a **skill package** designed for AI agent frameworks. You interact with it through natural language conversations with an AI agent, rather than through CLI commands or library imports.

### Which platforms does Tapestry support?

- **Zhihu** (知乎): Questions, answers, articles, profiles
- **Reddit**: Threads and discussions
- **Hacker News**: Discussions and comments
- **X (Twitter)**: Posts and threads
- **Xiaohongshu** (小红书): Notes and profiles
- **Weibo** (微博): Posts
- **Generic HTML**: Any webpage

See [Supported Platforms](reference/platforms.md) for details.

### Do I need programming experience?

No. Tapestry is designed to work through natural language conversations with AI agents. However, basic command-line familiarity is helpful for installation and troubleshooting.

## Installation & Setup

### How do I install Tapestry?

See the [Installation Guide](installation.md) for complete instructions. Quick version:

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Browser support
pip install -r requirements-browser.txt
playwright install chromium

# Install skill
cp -r skills/tapestry ~/.claude/skills/
```

### Do I need browser rendering?

Browser rendering is **optional but recommended**. Many modern websites use JavaScript heavily and won't work without it. Install Playwright for best results:

```bash
pip install -r requirements-browser.txt
playwright install chromium
```

### What are the system requirements?

**Minimum**:
- Python 3.8+
- 500MB disk space
- 2GB RAM

**Recommended**:
- Python 3.10+
- 2GB disk space
- 4GB RAM (for browser rendering)
- Linux, macOS, or Windows

### Can I use Tapestry without Claude Code?

Yes! Tapestry follows the Agent Skills specification and works with any compatible framework:
- Claude Code
- OpenClaw
- Codex
- Any framework supporting Agent Skills

## Usage Questions

### How do I capture a webpage?

```bash
cd skills/tapestry
python3 ingest/_scripts/run.py "https://example.com/article"
```

Or through Claude Code:
```
"Capture this article: https://example.com/article"
```

### Can I process multiple URLs at once?

Yes:

```bash
python3 ingest/_scripts/run.py \
  "https://example.com/page1" \
  "https://example.com/page2" \
  "https://example.com/page3"
```

### Where is captured content stored?

- **Raw HTML**: `data/captures/`
- **Structured JSON**: `data/feeds/`
- **Knowledge base notes**: `knowledge-base/`

### How do I search my knowledge base?

```bash
# Search catalog
grep "search term" knowledge-base/catalog.jsonl

# Or use the web viewer
python3 display/_scripts/publish_viewer.py
python3 -m http.server 8766 --directory knowledge-base/_viewer
```

### Can I export my knowledge base?

Yes, the knowledge base is just Markdown files and JSON. You can:
- Copy files directly
- Use with Obsidian, Notion, etc.
- Generate static websites
- Export to other formats

## Content Quality

### Why is extracted content so short?

Short content usually means:
1. **JavaScript rendering needed**: Install Playwright
2. **Wrong CSS selectors**: Content is in different elements
3. **Content behind login**: Tapestry can't access authenticated content

See [Troubleshooting: Short Content](reference/troubleshooting.md#short-content-extracted).

### How can I improve extraction quality?

1. **Install browser support**: `pip install -r requirements-browser.txt`
2. **Check the site**: View source to see if content is in HTML
3. **Add context**: Use `--text` to help AI understand intent
4. **Verify selectors**: Check if CSS selectors match actual HTML

### Does Tapestry handle paywalled content?

No. Tapestry only captures publicly accessible content. It doesn't handle:
- Login-required content
- Paywalled articles
- Private social media posts

### Can Tapestry capture images and videos?

Currently, Tapestry focuses on text content. Images and videos are noted in metadata but not downloaded. This is a planned feature for future releases.

## Privacy & Legal

### Where is my data stored?

All data is stored **locally** on your machine:
- `data/captures/` - Raw HTML
- `data/feeds/` - Structured JSON
- `knowledge-base/` - Markdown notes

Tapestry doesn't send data to external servers (except when fetching from source websites).

### Is web scraping legal?

Web scraping legality varies by jurisdiction and use case. Generally:

**Legal**:
- Publicly accessible content
- Personal use and research
- Respecting robots.txt
- Following rate limits

**Potentially problematic**:
- Bypassing authentication
- Ignoring robots.txt
- Commercial use without permission
- Excessive requests (DDoS)

**Tapestry's approach**:
- Only public content
- Respects robots.txt
- Rate limiting built-in
- User-agent identification

**Disclaimer**: This is not legal advice. Consult a lawyer for your specific situation.

### Will I get banned from platforms?

Risk is low if you:
- ✓ Use reasonable rate limits
- ✓ Only access public content
- ✓ Respect robots.txt
- ✓ Don't overwhelm servers

Tapestry includes rate limiting and follows best practices, but excessive use could still trigger anti-bot measures.

### Can I share my knowledge base?

Yes, it's your data. You can:
- Share with team members
- Publish as a website
- Commit to version control
- Export to other formats

However, respect original content licenses and attribution requirements.

## Technical Questions

### What's the difference between captures, feeds, and notes?

- **Captures** (`data/captures/`): Raw HTML from websites, for reproducibility
- **Feeds** (`data/feeds/`): Normalized JSON with structured data
- **Notes** (`knowledge-base/`): Human-readable Markdown with AI analysis

### How does the crawler system work?

1. **URL routing**: Match URL to platform-specific crawler
2. **Fetch**: Get HTML via HTTP or browser
3. **Parse**: Extract content using CSS selectors or readability
4. **Normalize**: Transform to standard schema
5. **Store**: Save as capture, feed, and note

See [Architecture Overview](architecture/overview.md) for details.

### Can I add support for new platforms?

Yes! See [Contributing Guide](../CONTRIBUTING.md) and [Crawler System](architecture/crawlers.md) for instructions.

Basic steps:
1. Create crawler class in `_src/crawlers/`
2. Define fetch and parse workflows
3. Register in `CrawlerRegistry`
4. Add schema spec in `feed/_specs/`

### How does AI synthesis work?

The synthesis skill:
1. Analyzes content using Claude
2. Extracts topics and themes
3. Determines appropriate chapter
4. Creates Markdown note
5. Updates indexes and catalog

This happens automatically after ingestion, or can be triggered manually.

### What's the performance like?

**HTTP mode** (fast):
- 1-2 seconds per URL
- Low memory usage
- Works for static sites

**Browser mode** (slow):
- 5-10 seconds per URL
- High memory usage (100-500MB per browser)
- Required for JavaScript sites

**Optimization tips**:
- Use HTTP when possible
- Process URLs in batches
- Reuse browser instances

## Troubleshooting

### I'm getting import errors

```bash
# Verify you're in the right directory
cd skills/tapestry

# Check dependencies
pip list | grep -E "httpx|pydantic|selectolax"

# Reinstall if needed
pip install -r requirements.txt
```

See [Troubleshooting: Import Errors](reference/troubleshooting.md#import-errors).

### Browser rendering isn't working

```bash
# Install Playwright
pip install playwright

# Install browser binaries
playwright install chromium

# Test
python3 -c "from playwright.async_api import async_playwright; print('OK')"
```

See [Troubleshooting: Browser Errors](reference/troubleshooting.md#browser-errors).

### Content extraction is failing

Common causes:
1. **JavaScript required**: Install Playwright
2. **Wrong selectors**: Check HTML structure
3. **Site blocking**: Try different user agent
4. **Network issues**: Check connectivity

See [Troubleshooting Guide](reference/troubleshooting.md) for solutions.

### How do I report a bug?

1. Check [existing issues](https://github.com/your-username/Tapestry/issues)
2. Gather information:
   - Python version
   - Error message
   - URL that failed
   - Steps to reproduce
3. [Open a new issue](https://github.com/your-username/Tapestry/issues/new)

## Comparison with Other Tools

### How is Tapestry different from web clippers?

**Web clippers** (Evernote, Notion):
- Save individual pages
- Manual organization
- Limited platform support
- Browser extension

**Tapestry**:
- Batch processing
- AI-powered organization
- Multi-platform support
- Command-line and AI agent interface

### How is Tapestry different from web scrapers?

**Traditional scrapers** (Scrapy, BeautifulSoup):
- Code-based configuration
- Manual selector definition
- No built-in organization
- Developer-focused

**Tapestry**:
- Natural language interface
- Automatic fallback chain
- AI-powered knowledge base
- User-friendly

### How is Tapestry different from bookmark managers?

**Bookmark managers** (Raindrop, Pocket):
- Store links only
- Basic tagging
- No content capture
- Cloud-based

**Tapestry**:
- Full content capture
- AI organization
- Local storage
- Knowledge base structure

## Future Plans

### What features are planned?

See [ROADMAP.md](../ROADMAP.md) for details. Highlights:
- Image and video capture
- More platform support
- Advanced search
- Collaboration features
- API improvements

### Can I request features?

Yes! [Open a feature request](https://github.com/your-username/Tapestry/issues/new?template=feature_request.md) or join the [discussion](https://github.com/your-username/Tapestry/discussions).

### How can I contribute?

See [Contributing Guide](../CONTRIBUTING.md). Ways to contribute:
- Add new platform crawlers
- Improve documentation
- Report bugs
- Share use cases
- Submit pull requests

## Getting Help

### Where can I get help?

1. **Documentation**: Start here
2. **Troubleshooting Guide**: [reference/troubleshooting.md](reference/troubleshooting.md)
3. **GitHub Issues**: Search existing issues
4. **GitHub Discussions**: Ask questions
5. **Community**: Join discussions

### How do I stay updated?

- Watch the [GitHub repository](https://github.com/your-username/Tapestry)
- Read [CHANGELOG.md](../CHANGELOG.md) for updates
- Follow [ROADMAP.md](../ROADMAP.md) for future plans

## Still Have Questions?

If your question isn't answered here:
1. Check the [full documentation](README.md)
2. Search [GitHub issues](https://github.com/your-username/Tapestry/issues)
3. Ask in [GitHub discussions](https://github.com/your-username/Tapestry/discussions)
4. [Open a new issue](https://github.com/your-username/Tapestry/issues/new)
