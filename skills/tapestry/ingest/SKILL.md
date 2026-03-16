---
name: ingest
description: Primitive web crawling and scraping for one or more URLs. Use when a user shares links, asks to ingest or archive web content, or needs raw source artifacts normalized into reusable local records before feed-building or synthesis.
argument-hint: [url-or-free-form-text]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Ingest

## When to use this skill

Use this skill when:
- A user shares URLs or links to web content
- You need to archive or ingest web content into the local knowledge base
- Raw source artifacts need to be normalized before feed-building or synthesis
- The user asks to "save", "archive", "ingest", or "capture" web content
- You need deterministic crawling and scraping before model-based analysis

## Overview

Turn a URL into a repeatable deterministic three-step chain:

1. capture the source
2. normalize it into a feed entry
3. store the resulting content in the local knowledge base

Use the bundled runner instead of hand-rolling fetch and parse steps in the conversation. This skill is the primitive acquisition layer: crawl the source, normalize the result, and persist durable artifacts. It does not perform model-based synthesis.
The runner auto-selects a crawler from the code-defined implementations under `_src/crawlers/`.

## Workflow

1. Collect every relevant URL from the current user request.
2. Resolve the skill-local runner relative to this `SKILL.md` file and run it:

```bash
python _scripts/run.py \
  "$ARGUMENTS"
```

3. Pass `--text` when the surrounding request text contains useful context worth preserving alongside the URLs.
4. Use `--list-crawlers` if you need to inspect the currently available crawler ids.
5. Use `--crawler <id>` only when the user explicitly wants to force a particular crawler instead of automatic matching.
6. Review the command output for the created feed, note, and handoff-ready artifacts.
7. **Synthesis behavior based on mode**:
   - `"auto"`: Agent evaluates note accumulation and decides whether to invoke `$tapestry-synthesis`. The decision should be based on:
     - Number of unmerged notes accumulated
     - Content relevance and importance
     - Whether immediate merge provides value vs. waiting for more content
     - System load and performance considerations
   - `"deterministic"`: Automatically invoke `$tapestry-synthesis` after every successful ingest
   - `"manual"`: Only invoke `$tapestry-synthesis` when user explicitly requests it
   - `"batch"`: Wait until user requests batch synthesis of multiple ingests
8. If the user wants a rigorous structured feed instead of the raw normalized artifact, route the next step through `$tapestry-feed`.
9. Report back with the successful URLs, created paths, matched crawlers when available, and any failures.

## Configuration

The behavior is controlled by `tapestry.config.json` at the project root:

```json
{
  "synthesis": {
    "mode": "auto",  // "auto", "manual", "batch", or "deterministic"
    "description": "Controls when synthesis runs after ingestion"
  }
}
```

**Modes**:
- `"auto"` (default): Agent evaluates note accumulation and decides whether to merge. This is intelligent and load-based, avoiding forced merge after every ingest.
- `"manual"`: Only synthesize when user explicitly requests it
- `"batch"`: Ingest multiple URLs, then synthesize all at once when requested
- `"deterministic"`: Automatically invoke synthesis after every successful ingest (high overhead, use cautiously)

## Operating Rules

- Batch URLs from the same request into one run unless the user explicitly wants them separated.
- Prefer the unified runner even for a single link so the full `URL -> crawler -> feed -> knowledge-base entry` path stays consistent.
- Do not manually fetch pages when the wrapper can run; reserve manual inspection for debugging failures.
- Do not perform high-level interpretation inside this skill. Hand that work off to a synthesis skill after deterministic ingest is complete.
- If the local CLI is missing or returns an error, surface the failure briefly and include the relevant stderr.

Include free-form request text when useful:

```bash
python _scripts/run.py \
  --text "Ingest these into the local KB for later synthesis" \
  "https://news.ycombinator.com/item?id=1" \
  "https://example.com/post"
```

## Output Expectations

Expect a compact result that makes the storage chain obvious:

- source URL
- feed artifact path when created
- knowledge-base note path when created
- matched crawler id when obvious
- analysis skill handoff when configured
- short status for failures

## Resource

- `_scripts/run.py`: extracts URLs from args, `--text`, or stdin and runs the unified crawler registry via the shared `_src` support code.
