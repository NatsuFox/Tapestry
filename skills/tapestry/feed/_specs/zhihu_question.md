# Feed Spec: Zhihu Question

## Applies to

- `workflow_id = zhihu_question`

## Intent

A Zhihu question page is a discussion prompt plus answer ecosystem. The feed should preserve:

- the core question
- the answer landscape
- any visible comment signals

## Priorities

1. exact question framing
2. top answers or answer clusters
3. visible engagement and follower counts
4. important comments when captured

## Output shape

### Source

- question URL
- question title
- answer count
- follower / visit counts when available

### Snapshot

- one-sentence question summary
- bullets for the dominant answer directions

### Primary Content

- `Question`
- `Top Answers / Representative Responses`

### Discussion / Response Signals

- `Answer Landscape`
- `Comment Signals` when available

### Media / Attachments

- mention if the page includes media or linked examples

### Structured Metadata

- answer count
- follower count
- visit count
- comment count

### Gaps / Uncertainties

- note if only a subset of answers was captured
