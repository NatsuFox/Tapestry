# Feed Spec: Hacker News Discussion

## Applies to

- `workflow_id = hackernews_discussion`

## Intent

A Hacker News item is not just an article. The feed should capture:

- the linked story or prompt
- the post framing
- the strongest argument threads in the comments
- notable corrections, caveats, or technical objections

## Priorities

1. what the linked story is about
2. why the thread exists
3. dominant positions in the discussion
4. corrections and dissent

## Output shape

### Source

- item URL
- linked title
- submitting author if captured
- publication time if available

### Snapshot

- one-sentence description of the story and thread
- bullets for the main argument threads

### Primary Content

- `Linked Story / Prompt`
- `Submission Context`
- `Key Technical Claims`

### Discussion / Response Signals

- `Dominant Viewpoints`
- `Corrections / Caveats`
- `Notable Comment Fragments`

### Media / Attachments

- usually `none` unless the linked item includes media references

### Structured Metadata

- comment count if available
- any top-level counts or extracted discussion signals

### Gaps / Uncertainties

- note if comments are truncated or if the linked story body was not captured
