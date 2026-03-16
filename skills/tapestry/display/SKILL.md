---
name: display
description: Expose the organized knowledge base through a readable frontend experience. Use when a user wants to browse the knowledge base visually as a lightweight site instead of reading raw Markdown files directly.
argument-hint: [optional-project-root]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Display

Publish a readable frontend for the knowledge base: **$ARGUMENTS**

## When to use this skill

Use this skill when:
- A user wants to browse the knowledge base visually
- You need to generate a readable frontend for the organized content
- The user asks to "view", "display", "publish", or "preview" the knowledge base
- A lightweight site presentation is preferred over raw Markdown files
- The user wants a blog-like or research portal view of the content

## Purpose

This skill acts as the presentation layer for the knowledge base.

It should:

- scan the `knowledge-base/` hierarchy
- preserve the topic and chapter structure defined by `index.md`
- generate a readable frontend that feels closer to a blog, notebook, or research portal than to a file browser

## Workflow

1. Resolve the project root from the argument if one is provided. Otherwise use the current working directory.
2. Ensure the knowledge-base hierarchy exists:

```bash
python ../synthesis/_scripts/bootstrap_kb.py
```

3. Publish the frontend bundle:

```bash
python _scripts/publish_viewer.py
```

4. If the user wants to preview it locally, serve the generated frontend directory:

```bash
python -m http.server 8766 --directory knowledge-base/_viewer
```

5. Report back with:
   - the output directory
   - the generated manifest path
   - the local preview URL if served

## Rules

- Treat the `index.md` hierarchy as the authoritative structural map.
- Do not flatten the topic/chapter tree into a single undifferentiated list.
- Preserve topic-level separation so semantically distant materials remain clearly separated.
- Make documents readable first, but keep enough structural information visible for navigation.
- If the knowledge base is sparse or incomplete, still generate the frontend and let empty sections remain honest rather than faking content.

## Resources

- `_scripts/publish_viewer.py`: scans `knowledge-base/`, copies frontend assets, and generates the JSON manifest.
- `_ui/`: custom static frontend assets for the viewer.
