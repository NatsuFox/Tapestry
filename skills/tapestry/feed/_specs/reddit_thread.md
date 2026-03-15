# Feed Spec: Reddit Thread

## Applies to

- `workflow_id = reddit_thread`

## Intent

A Reddit thread feed should separate:

- the original post
- the linked media or external link
- the comment ecosystem

## Priorities

1. original post title and core question/claim
2. linked media or destination
3. major answer clusters in the comments
4. especially concrete or authoritative replies

## Output shape

### Source

- thread URL
- subreddit
- post author
- publication time

### Snapshot

- one-sentence summary of the post
- bullets for the main reply patterns

### Primary Content

- `Original Post`
- `Linked Media / Link Target`

### Discussion / Response Signals

- `Top Response Themes`
- `Useful Identifications / Explanations`
- `High-Signal Comment Samples`

### Media / Attachments

- include linked image/media URL explicitly

### Structured Metadata

- score
- comment count
- post hint / media type

### Gaps / Uncertainties

- note deleted content, moderation notices, or crawler-side comment flattening limits
