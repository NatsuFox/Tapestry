# Feed Spec: Weibo Post

## Applies to

- `workflow_id = weibo_post`

## Intent

A Weibo post feed should preserve the public post wording and any visible public framing, while keeping platform chrome out of the final result as much as possible.

## Priorities

1. original post text
2. author/account identity
3. visible interaction counts
4. linked or embedded media

## Output shape

### Source

- post URL
- author/account
- time if available

### Snapshot

- one-sentence post summary
- bullets for public counts, key claim, and media

### Primary Content

- `Post Text`
- `Claim / Topic`

### Discussion / Response Signals

- include only if comments or repost context were actually captured

### Media / Attachments

- include image/video presence and media URLs when available

### Structured Metadata

- repost / comment / like counts if exposed
- platform-specific ids if captured

### Gaps / Uncertainties

- note if the page only exposed metadata and not the full discussion context
