# Feed Spec: Xiaohongshu Profile

## Applies to

- `workflow_id = xiaohongshu_profile`

## Intent

A Xiaohongshu profile feed should behave like a profile card, not like an article.

## Priorities

1. profile name / nickname
2. profile bio / description
3. visible interaction counts
4. surfaced recent-note titles
5. explicit platform limitations

## Output shape

### Source

- profile URL
- displayed profile name

### Snapshot

- one-sentence statement of who this account appears to be
- bullets for visible counts and profile signals

### Primary Content

- `Profile Identity`
- `Bio / Description`
- `Recent Visible Note Titles`

### Discussion / Response Signals

- usually brief or omitted

### Media / Attachments

- only include if the crawler exposed profile or note-cover media

### Structured Metadata

- follower-like counts
- account ids or red ids if available

### Gaps / Uncertainties

- this section is mandatory
- explicitly state if the platform served only a generic public shell instead of rich profile data
- do not pretend the profile is complete when the crawler only saw the platform shell
