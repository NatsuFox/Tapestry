# Feed Spec: Zhihu Profile

## Applies to

- `workflow_id = zhihu_profile`

## Intent

A Zhihu profile feed should function like a compact profile card plus account statistics.

## Priorities

1. name
2. headline / description
3. follower and activity counts
4. account scope signals such as answers and articles

## Output shape

### Source

- profile URL
- display name

### Snapshot

- one-sentence statement of who this user appears to be
- bullets for the key counts

### Primary Content

- `Identity`
- `Headline / Description`
- `Activity Profile`

### Discussion / Response Signals

- normally omitted unless comments or additional interaction context were actually captured

### Media / Attachments

- only include if profile media was captured

### Structured Metadata

- follower count
- following count
- answer count
- article count
- pins count

### Gaps / Uncertainties

- note when profile description is sparse or machine-like
