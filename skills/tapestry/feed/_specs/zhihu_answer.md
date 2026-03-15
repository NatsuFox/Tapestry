# Feed Spec: Zhihu Answer

## Applies to

- `workflow_id = zhihu_answer`

## Intent

A Zhihu answer feed should keep the answer as the main object, while preserving:

- the parent question
- the answerer identity
- the answer body
- the comment thread

## Priorities

1. parent question
2. answer body
3. answerer identity
4. vote/comment counts
5. comment discussion

## Output shape

### Source

- answer URL
- parent question title
- answer author
- publication time

### Snapshot

- one-sentence description of the answer’s main position
- bullets for the strongest arguments or examples

### Primary Content

- `Question Context`
- `Answer Body`

### Discussion / Response Signals

- `Vote / Engagement Signals`
- `Comment Highlights`

### Media / Attachments

- mention any linked media or notable referenced resources

### Structured Metadata

- voteup count
- comment count
- author headline

### Gaps / Uncertainties

- note if the body still contains page chrome around the answer
