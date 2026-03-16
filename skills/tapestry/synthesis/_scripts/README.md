# Synthesis Scripts

Scripts for the Tapestry synthesis workflow.

## Important: Working Directory

**These scripts must be run from the project root**, not from the skill directory. This ensures they can find the `data/` and `knowledge-base/` directories.

## Scripts

### load_context.py

Loads handoff context for a stored note or URL.

**Usage from project root**:
```bash
cd /root/Workspace/PROJECTS/powers/Tapestry
python skills/tapestry/synthesis/_scripts/load_context.py <url-or-note-path>
```

**Usage with --project-root flag**:
```bash
python skills/tapestry/synthesis/_scripts/load_context.py \
  --project-root /root/Workspace/PROJECTS/powers/Tapestry \
  <url-or-note-path>
```

**Examples**:
```bash
# By URL
python skills/tapestry/synthesis/_scripts/load_context.py https://example.com/article

# By note path
python skills/tapestry/synthesis/_scripts/load_context.py \
  knowledge-base/notes/2026/03/20260316T113405Z-overview.md
```

### bootstrap_kb.py

Creates the book-like knowledge base structure from the blueprint.

**Usage from project root**:
```bash
cd /root/Workspace/PROJECTS/powers/Tapestry
python skills/tapestry/synthesis/_scripts/bootstrap_kb.py
```

**Usage with --project-root flag**:
```bash
python skills/tapestry/synthesis/_scripts/bootstrap_kb.py \
  --project-root /root/Workspace/PROJECTS/powers/Tapestry
```

## Why Project Root?

These scripts need to access:
- `data/captures/` - Raw HTML captures
- `data/feeds/` - Normalized feed JSON
- `knowledge-base/catalog.jsonl` - Index of ingested content
- `knowledge-base/notes/` - Phase 1 notes

If run from the wrong directory, they will create these directories in the wrong place.

## Troubleshooting

**Error: "No stored catalog entry matched"**
- Make sure you're running from the project root
- Or use `--project-root` flag to specify the correct location
- Verify the URL or note path was actually ingested

**Directories created in wrong place**
- Delete the incorrectly created `data/` and `knowledge-base/` directories
- Run from project root or use `--project-root` flag
