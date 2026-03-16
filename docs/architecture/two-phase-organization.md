# Two-Phase Knowledge Organization

## Overview

Tapestry uses a **two-phase architecture** to organize web content into a knowledge base:

1. **Phase 1 (Ingest)**: Deterministic extraction → date-organized notes
2. **Phase 2 (Synthesis)**: AI-driven analysis → book-organized chapters

This separation ensures that raw data is preserved while allowing flexible, intelligent organization.

## Phase 1: Ingest (Deterministic)

**Purpose**: Capture and preserve raw content without interpretation

**Process**:
```bash
python skills/tapestry/ingest/_scripts/run.py <url>
```

**Output Structure**:
```
knowledge-base/
├── notes/                    # Date-organized raw notes
│   └── YYYY/
│       └── MM/
│           └── YYYYMMDDTHHMMSSZ-slug.md
└── catalog.jsonl            # Index of all ingested content

data/
├── captures/                # Raw HTTP/browser captures
│   └── YYYY/MM/...
└── feeds/                   # Normalized feed JSON
    └── YYYY/MM/...
```

**Characteristics**:
- No AI interpretation
- Chronological organization by ingest date
- Preserves all source material
- Creates deterministic baseline for synthesis

**What's stored**:
- Source URL and canonical URL
- Extracted title and body
- Comments (if applicable)
- Metadata and timestamps
- Analysis handoff instructions

## Phase 2: Synthesis (AI-Driven)

**Purpose**: Analyze content and organize into semantic book structure

**Process**:
```bash
# Invoked via the synthesis skill
$tapestry-synthesis <note-path-or-url>
```

**Output Structure**:
```
knowledge-base/
├── index.md                 # Top-level topic index
├── ai-and-research/
│   ├── index.md            # Topic index
│   ├── agent-development-and-tooling/
│   │   └── index.md        # Chapter content
│   ├── model-training-and-optimization/
│   │   └── index.md
│   └── research-tracking-and-papers/
│       └── index.md
├── markets-and-trading/
│   └── ...
└── notes/                   # Phase 1 notes remain unchanged
    └── YYYY/MM/...
```

**Characteristics**:
- AI-driven content analysis
- Semantic organization by topic/chapter
- Book-like hierarchical structure
- Synthesized, formatted content
- Maintains navigation via index.md files

**What happens**:
1. Load handoff context from Phase 1 note
2. Read governance rules and existing KB structure
3. Decide topic and chapter placement
4. Apply synthesis quality standards (formatting, cleanup, organization)
5. Create or extend chapter content
6. Update all parent index.md files

## Why Two Phases?

### Separation of Concerns

**Phase 1 (Deterministic)**:
- Fast, reliable, no API costs
- Preserves exact source material
- Can be re-synthesized differently later
- Provides audit trail

**Phase 2 (AI-Driven)**:
- Flexible semantic organization
- High-quality formatting and cleanup
- Contextual placement decisions
- Can evolve as KB grows

### Workflow Flexibility

Users can choose their workflow:

**Quick capture only**:
```bash
$tapestry-ingest <url>
# Stops after Phase 1
```

**Full analysis**:
```bash
$tapestry-ingest <url>
$tapestry-synthesis <url>
# Completes both phases
```

**Batch then organize**:
```bash
# Ingest many URLs quickly
$tapestry-ingest <url1> <url2> <url3>

# Later, synthesize selectively
$tapestry-synthesis <url1>
$tapestry-synthesis <url3>
```

## Directory Coexistence

Both structures coexist in `knowledge-base/`:

```
knowledge-base/
├── notes/              # Phase 1: chronological, immutable
│   └── 2026/03/...
├── ai-and-research/    # Phase 2: semantic, evolving
├── markets-and-trading/
├── people-and-profiles/
├── community-qa-and-discussion/
├── general-reference/
├── index.md            # Book navigation
└── catalog.jsonl       # Ingest index
```

**Key principle**: Phase 1 notes are never modified by Phase 2. They remain as the factual baseline.

## Synthesis Quality Standards

Phase 2 applies comprehensive quality standards:

1. **Text formatting**: Headers, paragraphs, markdown formatting
2. **Content cleanup**: Remove navigation, boilerplate, ads
3. **Organization**: Logical structure with clear hierarchy
4. **Factual accuracy**: Ground in source material only
5. **KB integration**: Proper topic/chapter placement

See [Synthesis Quality Standards](synthesis-quality-standards.md) for details.

## Governance

Phase 2 follows governance rules in `skills/tapestry/synthesis/_kb_rules/`:

- `_shared-governance.md`: Overall KB maintenance principles
- `topic-taxonomy.md`: When to create topics
- `chapter-decision-rules.md`: When to create/extend/split chapters

## Example Flow

### User ingests a URL:

```bash
$tapestry-ingest https://agentskills.io/home
```

**Result**:
- `knowledge-base/notes/2026/03/20260316T110840Z-overview.md` (raw note)
- `data/feeds/2026/03/20260316T110840Z-overview.json` (normalized feed)
- `data/captures/2026/03/20260316T110840Z-agentskills-io-home.json` (raw capture)
- Entry in `knowledge-base/catalog.jsonl`

### User requests synthesis:

```bash
$tapestry-synthesis https://agentskills.io/home
```

**Result**:
- Reads the Phase 1 note
- Analyzes content (about Agent Skills format)
- Determines placement: `ai-and-research/agent-development-and-tooling/`
- Creates new chapter with formatted, organized content
- Updates `ai-and-research/index.md` to include new chapter
- Phase 1 note remains unchanged

## Benefits

**Reliability**: Deterministic extraction ensures consistent baseline

**Flexibility**: Can re-synthesize with different strategies

**Auditability**: Original source material always available

**Scalability**: Fast ingest, selective synthesis

**Quality**: AI-driven formatting and organization

**Portability**: Both phases produce standard formats (JSON, Markdown)

## See Also

- [Architecture Overview](overview.md)
- [Content Pipeline](content-pipeline.md)
- [Synthesis Quality Standards](synthesis-quality-standards.md)
- [Directory Structure](directory-structure.md)
