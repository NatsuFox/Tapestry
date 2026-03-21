---
name: feed
description: Turn a crawler-produced Tapestry artifact into a source-appropriate structured feed. Use when a user wants a rigorous feed entry, normalized text output, or source-specific organization rather than a loose free-form summary.
argument-hint: [note-path-or-url]
allowed-tools: Bash(*), Read, Glob, Grep, Write, Edit
---

# Tapestry Feed

Build a structured feed entry for: **$ARGUMENTS**

## When to use this skill

Use this skill when:
- A user wants a rigorous, structured feed entry from ingested content
- You need source-appropriate normalized text output
- The user asks for a "feed", "structured output", or "formatted entry"
- Source-specific organization is needed rather than free-form summary
- Platform-native context (counts, tags, thread structure) should be preserved

## Purpose

This skill converts crawler-produced artifacts into a standardized but source-aware feed format.

The source-specific rules live in natural-language spec files under `feed/_specs/`. The Agent is expected to read the correct spec and then produce the feed text accordingly.

## Workflow

1. Identify the target note path or URL.
2. If the URL has not been ingested yet, run `$tapestry-ingest` first.
3. Resolve the stored artifact set:
   - read the Markdown note
   - read the feed JSON
   - read the capture JSON when the spec requires raw evidence
4. Determine the source type from `workflow_id` in the feed JSON.
5. Open the matching source spec in `feed/_specs/`.
6. Also read `feed/_specs/_shared-standard.md` before drafting the final feed.
7. Produce the final feed text exactly in the structure required by the source spec.

### Example: Building a feed from an ingested URL

```bash
# First, ensure the content is ingested
$tapestry-ingest "https://news.ycombinator.com/item?id=12345"

# Then build the structured feed
$tapestry-feed "https://news.ycombinator.com/item?id=12345"
```

### Example: Building a feed from a stored note

```bash
# Use the note path directly
$tapestry-feed "knowledge-base/notes/2024-01-15-hn-discussion.md"
```

## Rules

- The feed must be source-faithful, not generic.
- Use the same section order and emphasis required by the matching source spec.
- Do not invent facts missing from the crawler output.
- If a required field is missing, mark it explicitly as unknown or unavailable instead of fabricating it.
- Preserve important platform-native context such as counts, media, tags, thread structure, or profile signals when the source spec says they matter.
- If the user asks for narrative interpretation instead of a structured feed, route that work to `$tapestry-synthesis`.

## Source Specs

Read the correct file under `feed/_specs/` based on the `workflow_id`:

- `generic_html.md`
- `hackernews_discussion.md`
- `reddit_thread.md`
- `weibo_post.md`
- `x_post.md`
- `xiaohongshu_note.md`
- `xiaohongshu_profile.md`
- `zhihu_answer.md`
- `zhihu_profile.md`
- `zhihu_question.md`
- `zhihu_zhuanlan_article.md`

## Resources

- `feed/_specs/_shared-standard.md`: global rules that apply to every feed.
- `feed/_specs/_index.md`: quick map from source id to spec file.
