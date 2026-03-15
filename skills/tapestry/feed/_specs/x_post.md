# Feed Spec: X Post

## Applies to

- `workflow_id = x_post`

## Intent

An X post is short but context-dense. The feed should preserve the exact post substance, linked references, and visible author identity without over-expanding it.

## Priorities

1. exact post claim or statement
2. linked references or media hints
3. author identity
4. publication date label

## Output shape

### Source

- post URL
- author handle / name
- publication label or normalized time

### Snapshot

- one-sentence reformulation of the post
- bullets for:
  - main claim
  - referenced links
  - media hint if present

### Primary Content

- `Post Text`
- `Referenced Links`

### Discussion / Response Signals

- only include if reply or engagement data was captured
- otherwise say that no public reply structure was collected

### Media / Attachments

- mention attached image/video links if exposed by the source

### Structured Metadata

- tweet id / post id
- provider metadata from embed or other public endpoint

### Gaps / Uncertainties

- note when counts or replies were unavailable from the public surface
