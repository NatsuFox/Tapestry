# Advanced Workflows

Master complex Tapestry workflows for research, content curation, and knowledge management.

## Multi-URL Processing

### Batch Ingestion

Process multiple URLs efficiently:

```bash
python3 ingest/_scripts/run.py \
  "https://example.com/page1" \
  "https://example.com/page2" \
  "https://example.com/page3"
```

**Benefits**:
- Shared HTTP client (faster)
- Single browser instance (lower memory)
- Batch processing optimizations

### From File

Process URLs from a text file:

```bash
# Create URL list
cat > urls.txt <<EOF
https://example.com/page1
https://example.com/page2
https://example.com/page3
EOF

# Process all URLs
while read url; do
  python3 ingest/_scripts/run.py "$url"
done < urls.txt
```

### With Context

Add context to guide organization:

```bash
python3 ingest/_scripts/run.py \
  --text "Research on transformer architectures and attention mechanisms" \
  "https://arxiv.org/abs/1706.03762" \
  "https://jalammar.github.io/illustrated-transformer/" \
  "https://www.reddit.com/r/MachineLearning/comments/abc123/"
```

**Context helps**:
- AI understand your intent
- Better topic classification
- Improved chapter selection
- More relevant cross-references

## Research Workflows

### Literature Review

Collect and organize research papers:

```bash
# 1. Collect papers
python3 ingest/_scripts/run.py \
  --text "Survey of attention mechanisms in NLP" \
  "https://arxiv.org/abs/1706.03762" \
  "https://arxiv.org/abs/1810.04805" \
  "https://arxiv.org/abs/2005.14165"

# 2. Organize into knowledge base
# (Automatic via synthesis skill)

# 3. Generate summary
# Ask Claude: "Summarize the key findings from these papers"
```

### Topic Tracking

Monitor discussions on a specific topic:

```bash
# Collect from multiple platforms
python3 ingest/_scripts/run.py \
  --text "Tracking discussions on GPT-4 capabilities" \
  "https://news.ycombinator.com/item?id=123456" \
  "https://www.reddit.com/r/MachineLearning/comments/abc123/" \
  "https://x.com/username/status/123456" \
  "https://www.zhihu.com/question/123/answer/456"
```

### Expert Tracking

Follow specific researchers or creators:

```bash
# Collect profile and recent work
python3 ingest/_scripts/run.py \
  --text "Following AI researcher John Doe" \
  "https://www.zhihu.com/people/johndoe" \
  "https://johndoe.com/blog/recent-post" \
  "https://x.com/johndoe/status/123456"
```

## Content Curation

### Building a Resource Library

Create a curated collection on a topic:

```bash
# 1. Define scope
TOPIC="Modern web development best practices"

# 2. Collect diverse sources
python3 ingest/_scripts/run.py \
  --text "$TOPIC" \
  "https://web.dev/articles/best-practices" \
  "https://developer.mozilla.org/en-US/docs/Web/Guide" \
  "https://www.reddit.com/r/webdev/comments/abc123/" \
  "https://news.ycombinator.com/item?id=123456"

# 3. Review and organize
# Knowledge base automatically organized by synthesis skill

# 4. Add your notes
# Edit notes in knowledge-base/ to add commentary
```

### Weekly Digest

Create a weekly collection of interesting content:

```bash
# Create weekly collection script
cat > weekly_digest.sh <<'EOF'
#!/bin/bash
WEEK=$(date +%Y-W%U)
python3 ingest/_scripts/run.py \
  --text "Weekly digest $WEEK" \
  "$@"
EOF

chmod +x weekly_digest.sh

# Use it
./weekly_digest.sh \
  "https://news.ycombinator.com/item?id=123456" \
  "https://www.reddit.com/r/programming/comments/abc123/"
```

### Comparison Analysis

Compare different perspectives on a topic:

```bash
python3 ingest/_scripts/run.py \
  --text "Comparing views on AI safety" \
  "https://blog.anthropic.com/ai-safety" \
  "https://openai.com/research/ai-safety" \
  "https://www.reddit.com/r/ControlProblem/comments/abc123/" \
  "https://www.zhihu.com/question/123456"

# Then ask Claude:
# "Compare and contrast the different perspectives on AI safety from these sources"
```

## Platform-Specific Workflows

### Zhihu Deep Dive

Explore a Zhihu topic comprehensively:

```bash
# 1. Start with a question
python3 ingest/_scripts/run.py "https://www.zhihu.com/question/123456"

# 2. Collect top answers
python3 ingest/_scripts/run.py \
  "https://www.zhihu.com/question/123/answer/456" \
  "https://www.zhihu.com/question/123/answer/789"

# 3. Follow interesting authors
python3 ingest/_scripts/run.py \
  "https://www.zhihu.com/people/author1" \
  "https://www.zhihu.com/people/author2"

# 4. Collect related articles
python3 ingest/_scripts/run.py \
  "https://zhuanlan.zhihu.com/p/123456" \
  "https://zhuanlan.zhihu.com/p/789012"
```

### Reddit Thread Analysis

Archive and analyze Reddit discussions:

```bash
# Collect thread
python3 ingest/_scripts/run.py \
  "https://www.reddit.com/r/programming/comments/abc123/title/"

# Collect related threads
python3 ingest/_scripts/run.py \
  --text "Related discussions on topic X" \
  "https://www.reddit.com/r/programming/comments/def456/" \
  "https://www.reddit.com/r/coding/comments/ghi789/"
```

### Hacker News Discussion

Track HN discussions on a topic:

```bash
# Collect main discussion
python3 ingest/_scripts/run.py \
  "https://news.ycombinator.com/item?id=123456"

# Collect follow-up discussions
python3 ingest/_scripts/run.py \
  --text "Follow-up HN discussions" \
  "https://news.ycombinator.com/item?id=123457" \
  "https://news.ycombinator.com/item?id=123458"
```

### X (Twitter) Thread Collection

Archive Twitter threads:

```bash
# Collect thread starter
python3 ingest/_scripts/run.py \
  "https://x.com/username/status/123456"

# Collect thread replies (if separate URLs)
python3 ingest/_scripts/run.py \
  "https://x.com/username/status/123457" \
  "https://x.com/username/status/123458"
```

## Synthesis Workflows

### Automatic Organization

Let AI organize content automatically:

```bash
# 1. Ingest content
python3 ingest/_scripts/run.py \
  "https://example.com/article1" \
  "https://example.com/article2"

# 2. Synthesis happens automatically
# Content is analyzed and organized into knowledge base

# 3. Review organization
cat knowledge-base/index.md
```

### Manual Organization

Override automatic organization:

```bash
# 1. Ingest without synthesis
python3 ingest/_scripts/run.py \
  --no-synthesis \
  "https://example.com/article"

# 2. Manually place in knowledge base
mv data/feeds/20260316T103000Z_*.json \
   knowledge-base/custom-topic/custom-chapter/

# 3. Update indexes
python3 synthesis/_scripts/rebuild_indexes.py
```

### Batch Synthesis

Synthesize multiple feeds at once:

```bash
# 1. Collect feeds without synthesis
python3 ingest/_scripts/run.py --no-synthesis "URL1" "URL2" "URL3"

# 2. Batch synthesize
python3 synthesis/_scripts/batch_synthesize.py data/feeds/*.json
```

## Export Workflows

### Export to Markdown

Export knowledge base as flat markdown:

```bash
# Export all notes
python3 _scripts/export_markdown.py \
  --input knowledge-base/ \
  --output exports/markdown/
```

### Export to JSON

Export as structured JSON:

```bash
# Export catalog with full content
python3 _scripts/export_json.py \
  --input knowledge-base/ \
  --output exports/knowledge-base.json
```

### Export to CSV

Export catalog as CSV for analysis:

```bash
# Convert catalog to CSV
python3 -c "
import json
import csv

with open('knowledge-base/catalog.jsonl') as f:
    data = [json.loads(line) for line in f]

with open('catalog.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
"
```

### Export to Static Site

Generate a static website:

```bash
# Using display skill
python3 display/_scripts/publish_viewer.py

# Copy to web server
rsync -av knowledge-base/_viewer/ user@server:/var/www/kb/
```

## Automation Workflows

### Scheduled Collection

Automate regular content collection:

```bash
# Create cron job
cat > collect_daily.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y-%m-%d)
python3 ingest/_scripts/run.py \
  --text "Daily collection $DATE" \
  "https://news.ycombinator.com/best" \
  "https://www.reddit.com/r/programming/top/?t=day"
EOF

chmod +x collect_daily.sh

# Add to crontab (daily at 9am)
echo "0 9 * * * /path/to/collect_daily.sh" | crontab -
```

### RSS/Feed Monitoring

Monitor RSS feeds for new content:

```bash
# Create RSS monitor
cat > monitor_rss.sh <<'EOF'
#!/bin/bash
# Parse RSS feed and extract URLs
curl -s "https://example.com/feed.xml" | \
  grep -oP '(?<=<link>)[^<]+' | \
  while read url; do
    python3 ingest/_scripts/run.py "$url"
  done
EOF
```

### Bookmark Import

Import browser bookmarks:

```bash
# Export bookmarks from browser as HTML
# Then extract URLs
grep -oP '(?<=HREF=")[^"]+' bookmarks.html | \
  while read url; do
    python3 ingest/_scripts/run.py "$url"
  done
```

## Collaboration Workflows

### Shared Knowledge Base

Share knowledge base with team:

```bash
# 1. Initialize git repository
cd knowledge-base
git init
git add .
git commit -m "Initial knowledge base"

# 2. Push to shared repository
git remote add origin https://github.com/team/kb.git
git push -u origin main

# 3. Team members clone and contribute
git clone https://github.com/team/kb.git
```

### Review and Annotation

Add team annotations to notes:

```markdown
# Original Note

Content here...

---

## Team Notes

**@alice**: This relates to our Q3 project
**@bob**: See also internal doc XYZ
**@charlie**: Implemented this approach, works well
```

### Merge Multiple Knowledge Bases

Combine knowledge bases from multiple sources:

```bash
# 1. Copy all notes
cp -r kb1/knowledge-base/* knowledge-base/
cp -r kb2/knowledge-base/* knowledge-base/

# 2. Rebuild catalog
python3 synthesis/_scripts/rebuild_catalog.py

# 3. Rebuild indexes
python3 synthesis/_scripts/rebuild_indexes.py

# 4. Deduplicate
python3 _scripts/deduplicate.py knowledge-base/
```

## Performance Optimization

### Parallel Processing

Process URLs in parallel:

```bash
# Using GNU parallel
cat urls.txt | \
  parallel -j 4 python3 ingest/_scripts/run.py {}
```

### Selective Browser Rendering

Only use browser for JavaScript-heavy sites:

```bash
# HTTP-only for static sites (fast)
python3 ingest/_scripts/run.py \
  --fetch-mode http \
  "https://static-site.com/article"

# Browser for dynamic sites (slow but complete)
python3 ingest/_scripts/run.py \
  --fetch-mode browser \
  "https://spa-site.com/article"
```

### Caching

Cache fetched content to avoid re-fetching:

```bash
# Enable caching
export TAPESTRY_CACHE_DIR=/tmp/tapestry-cache

# Subsequent fetches use cache
python3 ingest/_scripts/run.py "https://example.com/article"
```

## Troubleshooting Workflows

### Retry Failed Ingestions

Retry URLs that failed:

```bash
# Find failed ingestions in logs
grep "ERROR" logs/ingest.log | \
  grep -oP 'https?://[^\s]+' | \
  while read url; do
    echo "Retrying: $url"
    python3 ingest/_scripts/run.py "$url"
  done
```

### Validate Content Quality

Check for low-quality extractions:

```bash
# Find short content
find data/feeds -name "*.json" -exec \
  python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(data.get('body', '')) < 500:
        print(sys.argv[1], len(data.get('body', '')))
" {} \;
```

### Regenerate Knowledge Base

Rebuild knowledge base from feeds:

```bash
# 1. Backup current KB
cp -r knowledge-base knowledge-base.backup

# 2. Clear KB
rm -rf knowledge-base/*

# 3. Regenerate from feeds
python3 synthesis/_scripts/rebuild_kb.py data/feeds/
```

## Best Practices

### Workflow Design

**Start small**:
- Begin with 5-10 URLs
- Verify quality
- Scale up gradually

**Add context**:
- Always use `--text` for better organization
- Be specific about your intent
- Include relevant keywords

**Review regularly**:
- Check knowledge base organization
- Adjust chapter structure as needed
- Remove outdated content

### Quality Control

**Verify extractions**:
```bash
# Check content length
jq '.body | length' data/feeds/*.json

# Check for missing fields
jq 'select(.title == null or .title == "")' data/feeds/*.json
```

**Monitor warnings**:
```bash
# Check for short content warnings
grep "suspiciously short" logs/ingest.log
```

### Organization

**Use consistent context**:
- Same context for related content
- Helps AI group content correctly

**Review auto-organization**:
- Check where content was placed
- Move if needed
- Update indexes

## Next Steps

- Learn about [Knowledge Base Organization](knowledge-base.md)
- Explore [Architecture Overview](../architecture/overview.md)
- Read [Troubleshooting Guide](../reference/troubleshooting.md)
