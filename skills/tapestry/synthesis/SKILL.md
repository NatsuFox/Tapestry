---
name: synthesis
description: Convert stored Tapestry artifacts into higher-level synthesis. Use when a user wants interpretation, consolidation, research notes, or analysis built on top of an already-ingested URL or note.
argument-hint: [note-path-or-url]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Synthesis

Analyze a stored Tapestry artifact: **$ARGUMENTS**

## When to use this skill

Use this skill when:
- A user wants interpretation or analysis of already-ingested content
- You need to consolidate multiple sources into research notes
- The user asks for synthesis, insights, or higher-level understanding
- You need to organize ingested content into the knowledge base hierarchy
- The deterministic ingest is complete and model-based reasoning is needed

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
2. **IMPORTANT**: Change to the project root directory before running the script:

```bash
cd /path/to/your/tapestry/project
python skills/tapestry/synthesis/_scripts/load_context.py \
  "$ARGUMENTS"
```

Or use the --project-root flag:

```bash
python _scripts/load_context.py \
  --project-root /path/to/your/tapestry/project \
  "$ARGUMENTS"
```

3. Read the returned handoff payload carefully:
   - `digest` is the deterministic baseline
   - `analysis.skill`, `analysis.instructions`, and `analysis.deliverable` describe the intended workflow
   - `note_text`, `feed_payload`, and `capture_payload` are the factual source materials
4. Ensure the book hierarchy exists:

```bash
cd /path/to/your/tapestry/project
python skills/tapestry/synthesis/_scripts/bootstrap_kb.py
```

Or use the --project-root flag:

```bash
python _scripts/bootstrap_kb.py \
  --project-root /path/to/your/tapestry/project
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

## Synthesis Quality Standards

**IMPORTANT**: All synthesized content must go through this refinement process, regardless of the source crawler or content type. These standards ensure consistent, high-quality output across all ingested content.

### 1. Text Formatting and Cleanup

**Add proper structure:**
- Use clear hierarchical headers (H2 for main sections, H3 for subsections)
- Add paragraph breaks for readability (no walls of text)
- Separate distinct topics with appropriate headers
- Use proper spacing after punctuation

**Apply markdown formatting:**
- `**bold**` for key terms and emphasis
- `*italic*` for technical terms or foreign words
- `` `code` `` for technical terms, commands, or code snippets
- `> quotes` for important statements or definitions
- `[links](url)` for all references and resources
- Lists (bulleted or numbered) for enumerated items

**Remove noise and artifacts:**
- Navigation text ("Home", "Next", "Previous", "Menu")
- Boilerplate ("Subscribe to our newsletter", "Cookie policy")
- Redundant disclaimers and legal text
- Advertisement content
- Broken formatting from HTML conversion
- Concatenated words or missing spaces

### 2. Content Organization

**Identify and structure:**
- What is the main topic or thesis?
- What are the key sections or concepts?
- What's the logical flow of information?

**Create clear hierarchy:**
- Start with a brief introduction or overview
- Group related concepts together
- Use descriptive section headers
- Maintain consistent heading levels

**Preserve important elements:**
- Technical details and specifications
- Code examples and commands
- Important links and references
- Author attributions and publication dates
- Key quotes and definitions

### 3. Factual Accuracy

**Ground in source material:**
- Only include information from the stored note, feed, or capture
- Maintain technical accuracy and proper terminology
- Preserve numerical data and statistics
- Keep important context and caveats

**Do not:**
- Add information not in the source
- Interpret or speculate beyond what's stated
- Simplify to the point of losing accuracy
- Change technical terms or jargon

### 4. Content-Specific Guidance

**For articles and documentation:**
- Preserve the main thesis and key arguments
- Highlight concrete claims and evidence
- Structure with clear sections
- Keep code examples and technical details

**For discussions and Q&A:**
- Preserve question-answer structure
- Highlight key insights from comments
- Note areas of consensus or disagreement
- Keep important context from the discussion

**For reference material:**
- Organize as a reference document
- Use clear section headers for easy lookup
- Preserve technical specifications
- Keep all links and resources

### 5. Knowledge Base Integration

**Determine placement:**
- Read existing KB structure before deciding
- Find the most appropriate topic/chapter
- Consider creating new sections if needed
- Maintain topical coherence

**Update hierarchy:**
- Add entry to parent `index.md`
- Update topic descriptions if needed
- Maintain navigation structure
- Follow governance rules in `_kb_rules/`

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
