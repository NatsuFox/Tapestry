---
name: export
description: Export knowledge base content to PDF, Markdown, or HTML files saved under _data/exports/. Use when a user wants to save or share KB content as downloadable files. Supports exporting a single document file, a single feed entry, a single note, or the entire knowledge base.
argument-hint: "[format: pdf|markdown|html|all] [scope: file|feed|note|kb] [target: path]"
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Export

Export knowledge base content to portable file formats: **$ARGUMENTS**

## When to use this skill

Use this skill when:
- A user wants to export, save, download, or share knowledge base content
- The user asks for a PDF, Markdown, or HTML version of a document or the whole KB
- The user wants offline-readable files from the knowledge base
- The user wants to share a chapter or article outside the viewer

## Arguments

The argument string may contain any combination of:

- **format**: `pdf`, `markdown`, `html`, or `all` (default: `all`)
- **scope**: `file`, `note`, `feed`, or `kb` (default: `kb`)
- **target**: a path or partial path to the target artifact (required for `file`, `note`, `feed` scopes)

Examples:
- `"pdf kb"` — export the entire knowledge base as PDF
- `"html file _data/books/ai/chapter.md"` — export one document as HTML
- `"all note _data/notes/2025/03/my-note.md"` — export one note in all three formats
- `"markdown feed _data/feeds/2025/03/abc123.json"` — export one feed entry as Markdown

## Scope Resolution

| Scope | Source files | Notes |
|---|---|---|
| `file` | Single `.md` file under `_data/books/` | Path provided by user |
| `note` | Single `.md` file under `_data/notes/` | Path provided by user |
| `feed` | Single `.json` file under `_data/feeds/` | Exports the `body` field as Markdown |
| `kb` | All `.md` files under `_data/books/` recursively | Entire knowledge base |

## Workflow

1. Parse the argument to determine format, scope, and target.
2. Change to the project root directory.
3. Run the export script:

```bash
# Export entire KB as PDF
python export/_scripts/export.py --format pdf --scope kb

# Export entire KB in all formats
python export/_scripts/export.py --format all --scope kb

# Export a single document as HTML
python export/_scripts/export.py --format html --scope file --target _data/books/topic/chapter/doc.md

# Export a single note as Markdown
python export/_scripts/export.py --format markdown --scope note --target _data/notes/2025/03/note.md

# Export a single feed entry in all formats
python export/_scripts/export.py --format all --scope feed --target _data/feeds/2025/03/abc123.json
```

4. The script prints a JSON summary of all exported file paths to stdout.
5. Report the output paths back to the user.

## Output Location

All exported files are saved under `_data/exports/`:

```
_data/exports/
  markdown/   ← .md files
  html/       ← standalone .html files (self-contained, with embedded images)
  pdf/        ← .pdf files (requires playwright)
```

File names mirror the source path structure. For example:
`_data/books/ai/chapter/doc.md` → `_data/exports/html/ai/chapter/doc.html`

## PDF Export Notes

PDF export uses Playwright (headless Chromium) to render the HTML to PDF.
If Playwright is not installed, the script falls back to saving a self-printing HTML file
(with `window.onload = window.print()`) and will notify the user to open it in a browser
and use Print → Save as PDF.

To install Playwright:
```bash
pip install playwright && playwright install chromium
```

## Rich Text Handling

- **Math (KaTeX)**: All exported HTML files include KaTeX CDN scripts for math rendering.
- **Images**: Images are base64-encoded and embedded inline in HTML/PDF exports for full portability.
- **Code blocks**: Syntax-highlighted HTML is preserved from the knowledge base renderer.
- **Tables**: Standard HTML tables are preserved.

## Resources

- `export/_scripts/export.py`: Main export script.
- `display/_scripts/publish_viewer.py`: Provides `render_markdown_document()` used for HTML rendering.
- `_src/config.py`: `TapestryConfig` for resolving project and data paths.
