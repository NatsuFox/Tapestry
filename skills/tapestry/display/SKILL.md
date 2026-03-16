---
name: display
description: Expose the organized knowledge base through a readable frontend experience. Use when a user wants to browse the knowledge base visually as a lightweight site instead of reading raw Markdown files directly. Supports building viewers for specific data paths (e.g., individual books) or the entire knowledge base.
argument-hint: [optional-data-path]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Display

Publish a readable frontend for the knowledge base: **$ARGUMENTS**

## When to use this skill

Use this skill when:
- A user wants to browse the knowledge base visually
- You need to generate a readable frontend for the organized content
- The user asks to "view", "display", "publish", or "preview" the knowledge base or a specific book
- A lightweight site presentation is preferred over raw Markdown files
- The user wants a blog-like or research portal view of the content

## Purpose

This skill acts as the presentation layer for the knowledge base.

It should:

- scan the specified data directory hierarchy (or default to `data/books/`)
- preserve the topic and chapter structure defined by `index.md`
- generate a readable frontend that feels closer to a blog, notebook, or research portal than to a file browser
- support building viewers for specific books or the entire knowledge base

## Workflow

1. Resolve the data path from the argument:
   - If a specific path is provided (e.g., "markets-and-trading"), use `data/books/markets-and-trading`
   - If no argument is provided, default to `data/books/` (entire knowledge base)

2. Ensure the data directory exists and contains markdown files

3. Publish the frontend bundle with the appropriate data path:

```bash
# For a specific book
python _scripts/publish_viewer.py --data-path data/books/markets-and-trading --force

# For the entire knowledge base (default)
python _scripts/publish_viewer.py --force
```

4. **IMPORTANT**: The viewer is created at `<data-path>/_viewer`. Before serving, ensure the data symlink exists:

```bash
# Navigate to the viewer directory
cd <data-path>/_viewer

# Create symlink if it doesn't exist (the viewer expects data/knowledge-base.json)
ln -sf "$(pwd)/data" data 2>/dev/null || true
```

5. Serve the generated frontend:

```bash
# Serve from the viewer directory
python -m http.server 8766 --directory <data-path>/_viewer
```

6. Report back with:
   - the data source path
   - the viewer output directory
   - the generated manifest path
   - the local preview URL if served

## Rules

- Treat the `index.md` hierarchy as the authoritative structural map.
- Do not flatten the topic/chapter tree into a single undifferentiated list.
- Preserve topic-level separation so semantically distant materials remain clearly separated.
- Make documents readable first, but keep enough structural information visible for navigation.
- If the knowledge base is sparse or incomplete, still generate the frontend and let empty sections remain honest rather than faking content.

## Common Issues

### Data Path Not Found

The frontend (`_ui/index.html`) expects to load `data/knowledge-base.json` relative to its location. If you see a JSON parsing error like "Unexpected token '<'", it means the data directory is missing.

**Solution**: Create a symlink from `_ui/data` to the actual data location:

```bash
ln -sf "$(pwd)/data/books/_viewer/data" _ui/data
```

This ensures the frontend can access the manifest and document data without duplicating files.

## Resources

- `_scripts/publish_viewer.py`: scans `knowledge-base/`, copies frontend assets, and generates the JSON manifest.
- `_ui/`: custom static frontend assets for the viewer.
