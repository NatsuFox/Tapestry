# Knowledge Base Organization

Learn how Tapestry organizes captured content into a structured, searchable knowledge base.

## Overview

Tapestry transforms raw web content into a **book-like knowledge base** with hierarchical organization, automatic indexing, and cross-referencing.

## Knowledge Base Structure

```
knowledge-base/
├── index.md                           # Root navigation
├── catalog.jsonl                      # Searchable index
├── ai-and-research/                   # Topic
│   ├── index.md                       # Topic overview
│   ├── research-tracking-and-papers/  # Chapter
│   │   ├── index.md                   # Chapter content
│   │   └── 20260316T103000Z-paper-title.md
│   └── model-training-and-optimization/
│       ├── index.md
│       └── 20260316T103100Z-training-guide.md
├── community-qa-and-discussion/
│   ├── index.md
│   └── platform-discussions/
│       ├── index.md
│       └── 20260316T103200Z-hn-discussion.md
└── people-and-profiles/
    ├── index.md
    └── researchers-and-creators/
        ├── index.md
        └── 20260316T103300Z-researcher-profile.md
```

## Hierarchy Levels

### 1. Root (knowledge-base/)

**Purpose**: Entry point to all knowledge

**Contains**:
- `index.md` - Main navigation with links to all topics
- `catalog.jsonl` - Searchable index of all notes

**Example index.md**:
```markdown
# Knowledge Base

## Topics

- [AI and Research](ai-and-research/index.md)
- [Community Q&A](community-qa-and-discussion/index.md)
- [People and Profiles](people-and-profiles/index.md)
```

### 2. Topics (Top-Level Categories)

**Purpose**: Broad subject areas

**Examples**:
- `ai-and-research/` - AI, ML, research papers
- `community-qa-and-discussion/` - Forum discussions, Q&A
- `markets-and-trading/` - Finance, trading, markets
- `people-and-profiles/` - User profiles, bios
- `general-reference/` - Miscellaneous articles

**Contains**:
- `index.md` - Topic overview and chapter links
- Chapter subdirectories

### 3. Chapters (Sub-Categories)

**Purpose**: Specific themes within topics

**Examples**:
- `research-tracking-and-papers/` - Academic papers
- `model-training-and-optimization/` - ML training guides
- `platform-discussions/` - Reddit, HN discussions
- `researchers-and-creators/` - Researcher profiles

**Contains**:
- `index.md` - Chapter overview and note links
- Individual note files

### 4. Notes (Individual Content)

**Purpose**: Single piece of captured content

**Naming**: `{timestamp}-{slug}.md`
- Timestamp: `20260316T103000Z` (ISO 8601)
- Slug: URL-friendly title

**Example**: `20260316T103000Z-how-transformers-work.md`

## Note Format

Each note follows a standard structure:

```markdown
# Article Title

**Source**: https://example.com/article
**Author**: John Doe
**Date**: 2026-03-16
**Platform**: generic_html

---

## Summary

AI-generated summary of the content...

## Content

Full article content with preserved formatting...

## Metadata

- **Topics**: AI, transformers, deep learning
- **Chapter**: ai-and-research/model-training-and-optimization
- **Related**: [Other Article](../other-article.md)
```

## Catalog System

### catalog.jsonl Format

Each line is a JSON object representing one note:

```json
{"path": "ai-and-research/research-tracking/20260316T103000Z-paper.md", "title": "Paper Title", "topics": ["AI", "research"], "timestamp": "2026-03-16T10:30:00Z", "url": "https://example.com", "platform": "generic_html"}
```

### Catalog Fields

- `path` - Relative path from knowledge-base/
- `title` - Note title
- `topics` - Array of topic tags
- `timestamp` - ISO 8601 timestamp
- `url` - Original source URL
- `platform` - Source platform

### Searching the Catalog

```bash
# Find all AI-related notes
grep '"AI"' knowledge-base/catalog.jsonl

# Find notes from specific date
grep '2026-03-16' knowledge-base/catalog.jsonl

# Find notes from specific platform
grep '"platform": "zhihu"' knowledge-base/catalog.jsonl
```

## Organization Rules

### Topic Selection

Content is organized by **semantic meaning**, not source platform:

**Good**:
- Zhihu answer about AI → `ai-and-research/`
- Reddit discussion about trading → `markets-and-trading/`
- HN discussion about startups → `community-qa-and-discussion/`

**Bad**:
- All Zhihu content → `zhihu/` (platform-based)
- All discussions → `discussions/` (format-based)

### Chapter Selection

Chapters group related content within a topic:

**AI and Research**:
- `research-tracking-and-papers/` - Academic papers, research updates
- `model-training-and-optimization/` - Training guides, optimization tips

**Community Q&A**:
- `platform-discussions/` - Reddit, HN, forum threads
- `practical-identification-and-qa/` - How-to questions, troubleshooting

### Automatic Organization

The synthesis skill automatically:

1. **Analyzes content** using AI
2. **Extracts topics and themes**
3. **Determines best chapter** based on semantic similarity
4. **Creates new chapters** if needed
5. **Updates all index files** for navigation
6. **Adds catalog entry** for searchability

## Navigation

### Index Files

Each level has an `index.md` that provides:

**Topic index.md**:
```markdown
# AI and Research

Overview of AI and research content...

## Chapters

- [Research Tracking](research-tracking-and-papers/index.md)
- [Model Training](model-training-and-optimization/index.md)
```

**Chapter index.md**:
```markdown
# Research Tracking and Papers

Recent research papers and updates...

## Notes

- [2026-03-16: Transformer Architecture](20260316T103000Z-transformers.md)
- [2026-03-15: Attention Mechanisms](20260315T143000Z-attention.md)
```

### Cross-References

Notes can reference each other:

```markdown
See also:
- [Related Paper](../other-chapter/20260315T103000Z-related.md)
- [Author Profile](../../people-and-profiles/researchers/20260314T103000Z-author.md)
```

## Browsing the Knowledge Base

### Command Line

```bash
# Navigate to knowledge base
cd skills/tapestry/knowledge-base

# View root index
cat index.md

# Browse a topic
cd ai-and-research
cat index.md

# Read a note
cat research-tracking/20260316T103000Z-paper.md
```

### Web Interface

Generate a browsable website:

```bash
# Generate viewer
python3 display/_scripts/publish_viewer.py

# Start web server
python3 -m http.server 8766 --directory knowledge-base/_viewer

# Open browser
open http://localhost:8766
```

**Features**:
- Clean, readable interface
- Topic and chapter navigation
- Search functionality
- Responsive design

### Text Editor

Open the knowledge-base/ directory in your editor:

```bash
# VS Code
code knowledge-base/

# Vim
vim knowledge-base/index.md

# Obsidian (if configured)
obsidian://open?vault=tapestry&file=knowledge-base/index.md
```

## Maintenance

### Adding Content

New content is automatically organized:

```bash
python3 ingest/_scripts/run.py "https://example.com/article"
# → Automatically placed in appropriate chapter
# → Index files updated
# → Catalog entry added
```

### Reorganizing Content

To move content between chapters:

1. **Move the note file**:
   ```bash
   mv ai-and-research/old-chapter/note.md ai-and-research/new-chapter/
   ```

2. **Update index files**:
   - Remove from old chapter's index.md
   - Add to new chapter's index.md

3. **Update catalog**:
   ```bash
   # Regenerate catalog
   python3 synthesis/_scripts/rebuild_catalog.py
   ```

### Cleaning Up

Remove outdated or duplicate content:

```bash
# Find duplicates by URL
grep -h '"url"' knowledge-base/catalog.jsonl | sort | uniq -d

# Remove a note
rm knowledge-base/topic/chapter/note.md

# Update indexes
python3 synthesis/_scripts/rebuild_indexes.py
```

## Best Practices

### Topic Design

**Keep topics broad**:
- ✓ `ai-and-research/` (broad)
- ✗ `transformer-papers/` (too specific)

**Use semantic categories**:
- ✓ `community-qa-and-discussion/` (semantic)
- ✗ `reddit-posts/` (platform-based)

### Chapter Design

**Keep chapters focused**:
- ✓ `research-tracking-and-papers/` (focused)
- ✗ `everything-ai/` (too broad)

**Use descriptive names**:
- ✓ `model-training-and-optimization/`
- ✗ `misc/`

### Note Naming

**Use descriptive slugs**:
- ✓ `20260316T103000Z-how-transformers-work.md`
- ✗ `20260316T103000Z-article.md`

**Keep slugs concise**:
- ✓ `transformer-architecture.md`
- ✗ `a-comprehensive-guide-to-understanding-transformer-architecture-in-deep-learning.md`

## Integration with Other Tools

### Obsidian

Configure Obsidian to use knowledge-base/ as a vault:

1. Open Obsidian
2. "Open folder as vault"
3. Select `skills/tapestry/knowledge-base/`

**Benefits**:
- Graph view of connections
- Backlinks
- Search
- Tags

### Notion

Export notes to Notion:

```bash
# Convert markdown to Notion format
python3 _scripts/export_to_notion.py
```

### Static Site Generator

Generate a static website:

```bash
# Using MkDocs
mkdocs build --config-file knowledge-base/mkdocs.yml

# Using Hugo
hugo --source knowledge-base/
```

## Advanced Features

### Tagging

Add tags to notes for better organization:

```markdown
---
tags: [AI, transformers, deep-learning, tutorial]
---
```

### Metadata

Enrich notes with custom metadata:

```markdown
---
difficulty: intermediate
reading_time: 15min
quality: high
---
```

### Templates

Use templates for consistent note structure:

```bash
# Create note from template
python3 synthesis/_scripts/create_note.py \
  --template research-paper \
  --title "Paper Title" \
  --url "https://example.com"
```

## Troubleshooting

### Notes in Wrong Chapter

**Problem**: Content organized incorrectly

**Solution**:
1. Move note to correct chapter
2. Update index files
3. Regenerate catalog

### Broken Links

**Problem**: Links between notes don't work

**Solution**:
```bash
# Find broken links
python3 _scripts/check_links.py knowledge-base/

# Fix relative paths
# Ensure links use correct relative paths
```

### Missing Index Files

**Problem**: Chapter missing index.md

**Solution**:
```bash
# Regenerate all indexes
python3 synthesis/_scripts/rebuild_indexes.py
```

## Next Steps

- Learn about [Advanced Workflows](advanced-workflows.md)
- Explore [Display Options](../architecture/overview.md#visualization)
- Read about [Synthesis Process](../architecture/content-pipeline.md#stage-7-synthesize-optional)
