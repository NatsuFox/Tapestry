# Architecture Overview

Tapestry is designed as a **three-layer content intelligence pipeline** that transforms raw web content into organized, searchable knowledge.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
│                    (URLs + Context)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: INGEST                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐         │
│  │  Fetch   │ -> │  Parse   │ -> │   Capture    │         │
│  │ (HTTP/   │    │ (CSS/    │    │  (Raw HTML)  │         │
│  │ Browser) │    │ Readab.) │    │              │         │
│  └──────────┘    └──────────┘    └──────────────┘         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Layer 2: FEED                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐         │
│  │ Platform │ -> │ Normalize│ -> │  Structured  │         │
│  │ Crawler  │    │  Schema  │    │     JSON     │         │
│  └──────────┘    └──────────┘    └──────────────┘         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Layer 3: SYNTHESIS                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐         │
│  │ Analyze  │ -> │ Organize │ -> │  Knowledge   │         │
│  │ (AI)     │    │ (Topics) │    │     Base     │         │
│  └──────────┘    └──────────┘    └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Three-Layer Design

### Layer 1: Ingest
**Purpose**: Capture raw web content reliably

- **Fetch**: Retrieve HTML using HTTP or browser rendering
- **Parse**: Extract content using CSS selectors or readability algorithms
- **Store**: Save raw HTML captures for reproducibility

**Output**: `data/captures/` - Raw HTML files

### Layer 2: Feed
**Purpose**: Normalize content into structured data

- **Platform Detection**: Identify content source (Zhihu, Reddit, HN, etc.)
- **Schema Mapping**: Transform to standardized JSON format
- **Validation**: Ensure data quality and completeness

**Output**: `data/feeds/` - Structured JSON files

### Layer 3: Synthesis
**Purpose**: Organize content into searchable knowledge

- **AI Analysis**: Extract themes, topics, and insights
- **Organization**: Build hierarchical knowledge base structure
- **Indexing**: Create searchable catalog and navigation

**Output**: `knowledge-base/` - Markdown notes with catalog

## Core Components

### Crawler Registry
Central registry of platform-specific crawlers:
- Zhihu (questions, answers, articles, profiles)
- X/Twitter (posts)
- Reddit (threads)
- Hacker News (discussions)
- Xiaohongshu (notes, profiles)
- Weibo (posts)
- Generic HTML (fallback)

### Ingestion Service
Orchestrates the fetch → parse → store pipeline:
- URL routing to appropriate crawler
- Fallback chain (HTTP → Readability → Browser)
- Content quality validation
- Duplicate detection

### Feed Normalization
Transforms platform-specific data to standard schema:
- Common fields: title, body, author, timestamp
- Platform metadata: votes, comments, tags
- Relationships: parent posts, replies, threads

### Knowledge Base Builder
Organizes content into book-like structure:
- Topic detection and clustering
- Chapter organization
- Cross-referencing
- Index generation

## Data Flow

```
URL Input
    ↓
[Crawler Registry] → Select crawler by URL pattern
    ↓
[Ingestion Service] → Fetch + Parse + Validate
    ↓
[Feed Storage] → Save structured JSON
    ↓
[Synthesis Engine] → AI analysis + Organization
    ↓
[Knowledge Base] → Markdown notes + Catalog
```

## Design Principles

### 1. Deterministic Pipeline
- Raw captures preserved for reproducibility
- Clear separation of facts (capture) vs interpretation (synthesis)
- Idempotent operations

### 2. Progressive Enhancement
- HTTP → Readability → Browser (fallback chain)
- Graceful degradation when dependencies unavailable
- Quality warnings for insufficient content

### 3. Platform Agnostic
- Unified schema across all platforms
- Extensible crawler system
- Generic HTML fallback

### 4. AI-Native Workflow
- Designed for agent frameworks (Claude Code, OpenClaw)
- Natural language interface
- Intelligent orchestration

## File Structure

```
skills/tapestry/
├── _src/                      # Shared code library
│   ├── registry.py           # Crawler registry
│   ├── ingest.py             # Ingestion service
│   ├── parse.py              # Content parsing
│   └── crawlers/             # Platform crawlers
│       ├── zhihu/
│       ├── reddit/
│       ├── hackernews/
│       └── generic_html/
├── ingest/                    # Ingestion sub-skill
│   ├── SKILL.md
│   └── _scripts/run.py
├── feed/                      # Feed sub-skill
│   ├── SKILL.md
│   └── _specs/               # Platform schemas
├── synthesis/                 # Synthesis sub-skill
│   ├── SKILL.md
│   └── _kb_blueprint/        # KB structure
├── display/                   # Display sub-skill
│   └── SKILL.md
├── data/                      # Generated data
│   ├── captures/             # Raw HTML
│   └── feeds/                # Structured JSON
└── knowledge-base/            # Final output
    ├── notes/                # Markdown notes
    └── catalog.jsonl         # Search index
```

## Technology Stack

### Core Dependencies
- **httpx**: Async HTTP client
- **pydantic**: Data validation and schemas
- **selectolax**: Fast HTML parsing
- **readability-lxml**: Content extraction

### Optional Dependencies
- **playwright**: Browser rendering for JavaScript sites

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatter
- **ruff**: Fast linter
- **mypy**: Type checking

## Extensibility

### Adding New Crawlers
1. Create crawler class in `_src/crawlers/`
2. Define fetch and parse workflows
3. Register in `CrawlerRegistry`
4. Add schema spec in `feed/_specs/`

### Custom Knowledge Base Structure
1. Modify `synthesis/_kb_blueprint/`
2. Update topic taxonomy
3. Adjust chapter decision rules

### Integration with Other Tools
- Export feeds to other formats (CSV, SQLite)
- Import from bookmarks or RSS
- Sync with note-taking apps

## Performance Considerations

### Fetch Strategy
- HTTP first (fast, low resource)
- Browser rendering only when needed (slow, high resource)
- Caching to avoid redundant fetches

### Parsing Optimization
- CSS selectors (fastest)
- Readability fallback (moderate)
- Browser rendering (slowest)

### Storage
- Compressed HTML captures
- Indexed JSON feeds
- Efficient catalog format

## Security & Privacy

### Data Handling
- All data stored locally
- No external API calls (except fetching content)
- User controls all data

### Content Capture
- Respects robots.txt
- Rate limiting to avoid overload
- User-agent identification

## Future Directions

See [ROADMAP.md](../../ROADMAP.md) for planned features and enhancements.
