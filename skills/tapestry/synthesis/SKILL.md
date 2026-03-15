---
name: tapestry-synthesis
description: Convert stored Tapestry artifacts into higher-level synthesis. Use when a user wants interpretation, consolidation, research notes, or analysis built on top of an already-ingested URL or note.
argument-hint: [note-path-or-url]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Synthesis

Analyze a stored Tapestry artifact: **$ARGUMENTS**

## Overview

This skill is the workflow layer for model-eligible reasoning.

Use it after deterministic ingest has already produced:

1. a capture JSON file
2. a normalized feed JSON file
3. a Markdown knowledge-base note
4. a structured handoff payload describing the recommended analysis

The package runtime does not call any model APIs directly. This skill owns the interpretation step.

This skill is also responsible for maintaining the book-like knowledge base under `knowledge-base/`.

## Workflow

1. Identify the target:
   - if the user gave a stored note path, use it directly
   - if the user gave a URL and it has not been ingested yet, run `$tapestry-ingest` first
2. Resolve the bundled handoff loader relative to this `SKILL.md` file and run it:

```bash
python _scripts/load_context.py \
  "$ARGUMENTS"
```

3. Read the returned handoff payload carefully:
   - `digest` is the deterministic baseline
   - `analysis.skill`, `analysis.instructions`, and `analysis.deliverable` describe the intended workflow
   - `note_text`, `feed_payload`, and `capture_payload` are the factual source materials
4. Ensure the book hierarchy exists:

```bash
python _scripts/bootstrap_kb.py
```

5. Read the knowledge-base governance files:
   - `_kb_rules/_shared-governance.md`
   - `_kb_rules/topic-taxonomy.md`
   - `_kb_rules/chapter-decision-rules.md`
6. Read the relevant `knowledge-base/.../index.md` files before deciding where this feed belongs.
7. Decide whether to:
   - create a new chapter
   - extend an existing chapter
   - restructure the topic tree
8. Perform the synthesis in the destination chapter index or chapter content area, while updating every affected parent `index.md`.
9. Return the synthesis clearly, grounded in the stored artifacts rather than vague recollection.

## Rules

- Treat the deterministic note and feed as the factual base layer.
- Do not fabricate claims that are not supported by the stored note, extracted body, or comments.
- Prefer high-signal synthesis over long paraphrase.
- If the user wants a standardized source-aware feed instead of an interpretive synthesis, use `$tapestry-feed` instead.
- If the user wants a visual frontend view of the organized knowledge base instead of a content update, use `$tapestry-display`.
- If the handoff payload has no configured skill or instructions, fall back to a concise grounded analysis.
- When persisting synthesis into the book-like knowledge base, never overwrite the deterministic ingest note.
- Every hierarchy level must keep a valid `index.md`.
- Top-level topics should stay coarse and semantically clean. If a feed no longer fits cleanly, restructure instead of forcing it.

## Resource

- `_scripts/load_context.py`: resolves a note path or URL into a normalized Tapestry handoff payload.
- `_scripts/bootstrap_kb.py`: creates missing `knowledge-base/` scaffolding with `index.md` at every level.
- `_kb_rules/`: natural-language governance for topic creation, chapter updates, and hierarchy adjustments.
- `_kb_blueprint/`: default `index.md` hierarchy used to initialize the book-like knowledge base.
