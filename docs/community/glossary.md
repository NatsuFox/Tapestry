# Glossary

Definitions of key terms used in Tapestry documentation.

## A

### Agent Framework
A software system that enables AI agents to perform tasks through natural language interaction. Examples: Claude Code, OpenClaw, Codex.

### Agent Skills
An open specification for giving AI agents new capabilities through modular skill packages. Tapestry follows this specification.

## B

### Browser Rendering
Using a headless browser (like Chromium via Playwright) to execute JavaScript and render dynamic web pages before extracting content.

## C

### Capture
The raw HTML content fetched from a URL, stored in `data/captures/` for reproducibility and reprocessing.

### Catalog
A searchable index of all knowledge base notes, stored as `knowledge-base/catalog.jsonl` with metadata for each note.

### Chapter
A sub-category within a topic in the knowledge base. Example: `research-tracking-and-papers/` is a chapter within `ai-and-research/`.

### Content Pipeline
The series of stages that transform a URL into organized knowledge: fetch → parse → validate → normalize → store → synthesize.

### Crawler
A platform-specific component that knows how to fetch and parse content from a particular website or service.

### Crawler Registry
A central registry that maps URL patterns to appropriate crawlers, enabling automatic crawler selection.

### CSS Selector
A pattern used to select HTML elements for content extraction. Example: `h1, .title` selects `<h1>` tags or elements with class "title".

## D

### Deterministic Pipeline
A processing pipeline that produces consistent, reproducible results given the same input, with clear separation between facts (captures) and interpretation (synthesis).

## F

### Fallback Chain
A sequence of extraction methods tried in order until one succeeds. Example: CSS selectors → Readability → Browser rendering → Metadata.

### Feed
Normalized, structured JSON representation of captured content, stored in `data/feeds/` following a standard schema.

### Fetch
The process of retrieving HTML content from a URL, either via HTTP request or browser rendering.

### FetchMode
The method used to retrieve content: `http` (standard request) or `browser` (headless browser rendering).

## H

### HTTP Fetch
Retrieving content using standard HTTP requests without JavaScript execution. Fast but limited to server-side rendered content.

## I

### Ingest
The process of capturing content from a URL, including fetching, parsing, and storing.

### Ingestion Service
The core service that orchestrates the fetch → parse → store pipeline for URL ingestion.

## K

### Knowledge Base
A hierarchical, book-like structure of organized content with topics, chapters, and notes, stored in `knowledge-base/`.

## M

### Metadata Extraction
Extracting content from HTML meta tags (Open Graph, Twitter Cards, etc.) as a last-resort fallback when other methods fail.

## N

### Note
A single Markdown file in the knowledge base representing one piece of captured content, with AI-generated analysis and organization.

### Normalization
The process of transforming platform-specific data into a standard schema with common fields (title, body, author, etc.).

## P

### Parse
The process of extracting structured content (title, body, author, etc.) from raw HTML.

### Platform
A specific website or service that Tapestry can crawl. Examples: Zhihu, Reddit, Hacker News, X (Twitter).

### Playwright
A browser automation library used by Tapestry for rendering JavaScript-heavy websites.

## R

### Readability
Mozilla's content extraction algorithm that identifies and extracts the main content from web pages using heuristics.

### Registry
See Crawler Registry.

## S

### Schema
A standardized data structure defining the fields and types for normalized content. Each platform has a schema spec in `feed/_specs/`.

### Selector
See CSS Selector.

### Skill
A modular capability package for AI agents, defined by a `SKILL.md` file describing workflows and behaviors.

### Slug
A URL-friendly version of a title used in filenames. Example: "How Transformers Work" → `how-transformers-work`.

### Synthesis
The process of using AI to analyze content, extract topics, determine organization, and create knowledge base notes.

## T

### Topic
A top-level category in the knowledge base. Examples: `ai-and-research/`, `community-qa-and-discussion/`, `people-and-profiles/`.

### Timestamp
An ISO 8601 formatted date-time string used in filenames and metadata. Example: `20260316T103000Z`.

## U

### URL Routing
The process of matching a URL to the appropriate crawler based on regex patterns.

## W

### Workflow
A sequence of steps defining how a task is performed. Tapestry uses workflows for fetching, parsing, and synthesis.

### WorkflowFetch
A configuration object defining how content should be fetched (mode, timeout, headers, etc.).

### WorkflowParse
A configuration object defining how content should be parsed (CSS selectors, fallback options, etc.).

## Common Abbreviations

- **API**: Application Programming Interface
- **CSS**: Cascading Style Sheets
- **HTML**: HyperText Markup Language
- **HTTP**: HyperText Transfer Protocol
- **JSON**: JavaScript Object Notation
- **JSONL**: JSON Lines (one JSON object per line)
- **KB**: Knowledge Base
- **MD**: Markdown
- **OG**: Open Graph (metadata protocol)
- **SPA**: Single-Page Application
- **URL**: Uniform Resource Locator

## File Extensions

- `.html`: HTML document
- `.json`: JSON data file
- `.jsonl`: JSON Lines file (one JSON object per line)
- `.md`: Markdown document
- `.py`: Python source file

## Directory Names

- `_src/`: Shared source code library
- `_specs/`: Specification documents
- `_scripts/`: Executable scripts
- `_tests/`: Unit tests
- `_kb_blueprint/`: Knowledge base structure template
- `_kb_rules/`: Knowledge base organization rules
- `data/`: Generated data (captures, feeds)
- `knowledge-base/`: Organized knowledge base

## Common Patterns

### Filename Patterns

**Captures and Feeds**:
```
{timestamp}_{platform}_{content_type}_{id}.{ext}
20260316T103000Z_zhihu_answer_123456.json
```

**Notes**:
```
{timestamp}-{slug}.md
20260316T103000Z-how-transformers-work.md
```

### URL Patterns

**Zhihu**:
- Question: `zhihu.com/question/{id}`
- Answer: `zhihu.com/question/{qid}/answer/{aid}`
- Article: `zhuanlan.zhihu.com/p/{id}`

**Reddit**:
- Thread: `reddit.com/r/{subreddit}/comments/{id}/{slug}/`

**Hacker News**:
- Discussion: `news.ycombinator.com/item?id={id}`

**X (Twitter)**:
- Post: `x.com/{username}/status/{id}`

## Related Concepts

### Content Extraction
The process of identifying and extracting meaningful content from HTML, using methods like CSS selectors, readability algorithms, or metadata.

### Web Scraping
The automated process of extracting data from websites. Tapestry is a specialized web scraping tool focused on content capture and organization.

### Knowledge Management
The practice of organizing, storing, and retrieving information effectively. Tapestry provides tools for knowledge management through its knowledge base system.

### Natural Language Processing (NLP)
Using AI to understand and process human language. Tapestry uses NLP for content analysis and organization.

## See Also

- [Architecture Overview](architecture/overview.md) - System design
- [Content Pipeline](architecture/content-pipeline.md) - Processing stages
- [Crawler System](architecture/crawlers.md) - Platform crawlers
- [FAQ](FAQ.md) - Frequently asked questions
