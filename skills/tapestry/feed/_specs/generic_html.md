# Feed Spec: Generic HTML

## Applies to

- `workflow_id = generic_html`

## Intent

Use this for ordinary article-like pages where there is no richer platform-specific structure.

## Priorities

1. article thesis
2. strongest factual claims
3. key named entities or topics
4. any directly useful takeaways

## Section emphasis

- `Snapshot`: thesis plus 3 to 5 concrete claims
- `Primary Content`: organize into `Thesis`, `Key Points`, `Useful Details`
- `Discussion / Response Signals`: only include if comments exist
- `Media / Attachments`: usually brief

## Output shape

### Source

- URL
- title
- author
- publication time if available

### Snapshot

- one-sentence summary
- bullets for strongest claims

### Primary Content

- `Thesis`
- `Key Points`
- `Useful Details`

### Discussion / Response Signals

- include only if comments were captured

### Media / Attachments

- mention linked media or image presence if available

### Structured Metadata

- tags or metadata fields from the crawler

### Gaps / Uncertainties

- note if the body appears partial or heavily UI-polluted
