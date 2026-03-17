# Supported Platforms

Tapestry provides native support for major content platforms with specialized crawlers.

## Platform Overview

| Platform | Content Types | Browser Required | Status |
|----------|--------------|------------------|--------|
| Zhihu | Questions, Answers, Articles, Profiles | No | ✓ Stable |
| Reddit | Threads, Comments | No | ✓ Stable |
| Hacker News | Discussions | No | ✓ Stable |
| X (Twitter) | Posts | Yes | ✓ Stable |
| Xiaohongshu | Notes, Profiles | Yes | ✓ Stable |
| Weibo | Posts | Yes | ✓ Stable |
| WeChat | Official Account Articles | No | ✓ Stable |
| Generic HTML | Any webpage | Optional | ✓ Stable |

## Zhihu (知乎)

### Supported Content Types

#### Questions
**URL Pattern**: `zhihu.com/question/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://www.zhihu.com/question/123456"
```

**Extracted Data**:
- Question title
- Question description
- Answer count
- Follower count
- Top answers (if available)

#### Answers
**URL Pattern**: `zhihu.com/question/*/answer/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://www.zhihu.com/question/123/answer/456"
```

**Extracted Data**:
- Question title (context)
- Answer content
- Author name
- Vote count
- Comment count
- Timestamp

#### Articles (Zhuanlan)
**URL Pattern**: `zhuanlan.zhihu.com/p/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://zhuanlan.zhihu.com/p/123456"
```

**Extracted Data**:
- Article title
- Article content
- Author name
- Like count
- Comment count
- Timestamp

#### Profiles
**URL Pattern**: `zhihu.com/people/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://www.zhihu.com/people/username"
```

**Extracted Data**:
- User name
- Bio/headline
- Follower count
- Answer count
- Article count

### Technical Details

**Fetch Mode**: HTTP (fast)
**Parse Method**: CSS selectors
**Browser Required**: No

**Selectors**:
- Title: `.QuestionHeader-title`, `.Post-Title`
- Body: `.RichContent-inner`, `.Post-RichTextContainer`
- Author: `.AuthorInfo-name`

## Reddit

### Supported Content Types

#### Threads
**URL Pattern**: `reddit.com/r/*/comments/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://www.reddit.com/r/programming/comments/abc123/title/"
```

**Extracted Data**:
- Post title
- Post body
- Author username
- Subreddit
- Upvote count
- Comment count
- Timestamp
- Top comments (if available)

### Technical Details

**Fetch Mode**: HTTP (fast)
**Parse Method**: CSS selectors
**Browser Required**: No

**Selectors**:
- Title: `[slot="title"]`
- Body: `[slot="text-body"]`
- Author: `[slot="authorName"]`

## Hacker News

### Supported Content Types

#### Discussions
**URL Pattern**: `news.ycombinator.com/item?id=*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://news.ycombinator.com/item?id=123456"
```

**Extracted Data**:
- Story title
- Story URL (if link post)
- Story text (if text post)
- Author username
- Points
- Comment count
- Timestamp
- Comments

### Technical Details

**Fetch Mode**: HTTP (fast)
**Parse Method**: CSS selectors
**Browser Required**: No

**Selectors**:
- Title: `.titleline > a`
- Body: `.toptext`
- Comments: `.comment`

## X (Twitter)

### Supported Content Types

#### Posts
**URL Pattern**: `x.com/*/status/*` or `twitter.com/*/status/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://x.com/username/status/123456"
```

**Extracted Data**:
- Tweet text
- Author username
- Author display name
- Timestamp
- Like count
- Retweet count
- Reply count
- Media (if available)

### Technical Details

**Fetch Mode**: Browser rendering (required)
**Parse Method**: CSS selectors
**Browser Required**: Yes

**Why Browser Required**: X heavily relies on JavaScript for content rendering.

## Xiaohongshu (小红书)

### Supported Content Types

#### Notes
**URL Pattern**: `xiaohongshu.com/explore/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://www.xiaohongshu.com/explore/123456"
```

**Extracted Data**:
- Note title
- Note content
- Author name
- Like count
- Comment count
- Timestamp
- Tags

#### Profiles
**URL Pattern**: `xiaohongshu.com/user/profile/*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://www.xiaohongshu.com/user/profile/123456"
```

**Extracted Data**:
- User name
- Bio
- Follower count
- Note count

### Technical Details

**Fetch Mode**: Browser rendering (required)
**Parse Method**: CSS selectors
**Browser Required**: Yes

**Why Browser Required**: Xiaohongshu uses heavy JavaScript rendering.

## Weibo (微博)

### Supported Content Types

#### Posts
**URL Pattern**: `weibo.com/*/[A-Z0-9]*`

**Example**:
```bash
python3 ingest/_scripts/run.py "https://weibo.com/123456/ABC123"
```

**Extracted Data**:
- Post content
- Author name
- Timestamp
- Like count
- Repost count
- Comment count

### Technical Details

**Fetch Mode**: Browser rendering (required)
**Parse Method**: CSS selectors
**Browser Required**: Yes

**Why Browser Required**: Weibo requires JavaScript for content loading.

## Generic HTML

### Supported Content Types

#### Any Webpage
**URL Pattern**: `*` (matches everything)

**Example**:
```bash
python3 ingest/_scripts/run.py "https://blog.example.com/article"
```

**Extracted Data**:
- Page title
- Main content
- Author (if available)
- Metadata

### Technical Details

**Fetch Mode**: HTTP with browser fallback
**Parse Method**: CSS selectors → Readability → Metadata
**Browser Required**: Optional (recommended for JavaScript sites)

**Selectors**:
- Title: `h1, .title, [class*='title']`
- Body: `article, main, .content, [role='main']`

**Fallback Chain**:
1. CSS selectors
2. Readability extraction
3. Browser rendering (if insufficient)
4. Metadata extraction

### Best For

- Blog posts
- Documentation sites
- News articles
- Static websites

### Not Ideal For

- Single-page applications (use browser rendering)
- Login-required content
- Dynamic content (use browser rendering)

## Platform Comparison

### Speed

**Fast** (< 1 second):
- Zhihu
- Reddit
- Hacker News
- WeChat Official Account
- Generic HTML (HTTP mode)

**Slow** (3-10 seconds):
- X (Twitter)
- Xiaohongshu
- Weibo
- Generic HTML (browser mode)

### Resource Usage

**Low**:
- Zhihu
- Reddit
- Hacker News
- WeChat Official Account

**High**:
- X (Twitter)
- Xiaohongshu
- Weibo

### Content Quality

**Excellent** (structured, complete):
- Zhihu
- Reddit
- Hacker News
- WeChat Official Account

**Good** (mostly complete):
- X (Twitter)
- Xiaohongshu
- Weibo

**Variable** (depends on site):
- Generic HTML

## Adding New Platforms

Want support for a new platform? See [Contributing Guide](../../CONTRIBUTING.md) for how to add new crawlers.

**Requirements**:
1. URL pattern for matching
2. Fetch strategy (HTTP or browser)
3. CSS selectors or parse logic
4. Schema definition

**Example**: Adding support for Medium

```python
# _src/crawlers/medium/__init__.py

class MediumCrawler(BaseCrawler):
    fetch = WorkflowFetch(mode=FetchMode.http)
    parse = WorkflowParse(
        title="h1",
        body="article",
        author=".author-name",
    )
```

See [Crawler System](../architecture/crawlers.md) for detailed instructions.
