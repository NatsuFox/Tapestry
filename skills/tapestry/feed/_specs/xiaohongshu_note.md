# Feed Spec: Xiaohongshu Note

## Applies to

- `workflow_id = xiaohongshu_note`

## Intent

A Xiaohongshu note often mixes:

- a catchy title
- a long descriptive body
- tags
- strong image/media signals

The feed should preserve those elements as a practical, structured note rather than flattening them into a generic article summary.

## Priorities

1. note title
2. full note description / body
3. author identity
4. tags
5. image set
6. visible interaction metadata

## Output shape

### Source

- note URL
- note title
- author
- publication time

### Snapshot

- one-sentence note summary
- bullets for the central topic, strongest claims/tips, and visible engagement

### Primary Content

- `Title`
- `Body`
- `Tags`

### Discussion / Response Signals

- include only if comments were captured
- otherwise say that comment content was not collected

### Media / Attachments

- this section is important
- include image count
- list image URLs or image references in order
- indicate live-photo presence when present

### Structured Metadata

- interaction info
- author token / note id if captured
- tag metadata

### Gaps / Uncertainties

- note when the platform served a restricted shell instead of full note data
