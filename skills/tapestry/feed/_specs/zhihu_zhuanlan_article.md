# Feed Spec: Zhihu Column Article

## Applies to

- `workflow_id = zhihu_zhuanlan_article`

## Intent

A Zhihu column article should read like a long-form authored post, with:

- title
- author
- article body
- visible engagement counts

## Priorities

1. article thesis
2. body structure
3. author framing
4. vote/comment counts

## Output shape

### Source

- article URL
- article title
- author
- publication time if available

### Snapshot

- one-sentence thesis
- bullets for the strongest takeaways

### Primary Content

- `Article Thesis`
- `Main Argument`
- `Supporting Points`

### Discussion / Response Signals

- usually just visible counts unless comments were actually captured

### Media / Attachments

- mention if images or embeds are present in the crawler output

### Structured Metadata

- voteup count
- comment count
- excerpt

### Gaps / Uncertainties

- note any remaining UI text leakage if the body is not perfectly cleaned
