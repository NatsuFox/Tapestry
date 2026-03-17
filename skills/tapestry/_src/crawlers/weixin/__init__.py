"""WeChat Official Account (mp.weixin.qq.com) crawler with full comment tree support."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from _src.models import (
    AnalysisHandoff,
    CapturedPage,
    FeedComment,
    FeedEntry,
    FetchMode,
    WorkflowKnowledgeBase,
    WorkflowMeta,
    WorkflowProfile,
)
from _src.registry import CrawlerDefinition, CrawlerProduct
from _src.router import normalize_url


def _workflow() -> WorkflowProfile:
    return WorkflowProfile(
        id="weixin_article",
        meta=WorkflowMeta(
            title="WeChat Official Account Article",
            description="Reverse-engineered WeChat article crawler with full metadata and comments.",
            content_type="article",
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Write a grounded synthesis of the WeChat article.",
            instructions=(
                "Use the stored WeChat article artifacts as the factual base layer.\n"
                "Include key metadata like view counts, likes, and publication time.\n"
                "Summarize comment discussions if present."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="weixin-articles"),
    )


def _extract_metadata(html: str) -> dict:
    """Extract metadata from JavaScript variables in HTML."""
    metadata = {}

    # Extract timestamp (var ct = "timestamp")
    ct_match = re.search(r'var ct = "(\d+)"', html)
    if ct_match:
        timestamp = int(ct_match.group(1))
        metadata['publish_timestamp'] = timestamp
        metadata['publish_time'] = datetime.fromtimestamp(timestamp, tz=timezone.utc)

    # Extract view count (var appmsg_read_num = "count")
    read_match = re.search(r'var appmsg_read_num = "(\d+)"', html)
    if read_match:
        metadata['read_count'] = int(read_match.group(1))

    # Extract like count (var appmsg_like_num = "count")
    like_match = re.search(r'var appmsg_like_num = "(\d+)"', html)
    if like_match:
        metadata['like_count'] = int(like_match.group(1))

    # Extract comment count
    comment_match = re.search(r'var comment_count = "(\d+)"', html)
    if comment_match:
        metadata['comment_count'] = int(comment_match.group(1))

    return metadata


def _extract_comments(html: str) -> list[FeedComment]:
    """Extract comment tree from HTML/JavaScript data."""
    comments = []

    # WeChat comments are often loaded via AJAX, but initial data might be in page
    # Look for comment data in JavaScript variables
    comment_data_match = re.search(r'var comment_list = (\[.*?\]);', html, re.DOTALL)
    if comment_data_match:
        try:
            comment_list = json.loads(comment_data_match.group(1))
            for item in comment_list:
                if isinstance(item, dict):
                    text = item.get('content', '').strip()
                    author = item.get('nick_name', '')
                    if text:
                        comments.append(FeedComment(author=author, text=text))

                        # Extract replies if present
                        replies = item.get('reply_list', [])
                        for reply in replies:
                            if isinstance(reply, dict):
                                reply_text = reply.get('content', '').strip()
                                reply_author = reply.get('nick_name', '')
                                if reply_text:
                                    comments.append(FeedComment(
                                        author=reply_author,
                                        text=f"↳ {reply_text}"
                                    ))
        except json.JSONDecodeError:
            pass

    return comments


async def crawl(
    url: str,
    target_root: Path,
    crawler: CrawlerDefinition,
    fetcher,
    parser,
) -> CrawlerProduct:
    """Crawl WeChat article with full metadata and comment tree."""

    # Headers from HAR analysis - critical for avoiding bot detection
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }

    # Fetch the page using httpx
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        final_url = str(response.url)
        status_code = response.status_code

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract title
    title_tag = soup.find('h1', class_='rich_media_title')
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # Extract author
    author_tag = (
        soup.find('a', class_='rich_media_meta_link') or
        soup.find('span', class_='rich_media_meta rich_media_meta_text') or
        soup.find('a', id='js_name')
    )
    author = author_tag.get_text(strip=True) if author_tag else None

    # Extract main content
    content_tag = soup.find('div', class_='rich_media_content')
    content_text = content_tag.get_text(strip=True) if content_tag else ""

    # Extract metadata
    metadata = _extract_metadata(html)

    # Extract comments
    comments = _extract_comments(html)

    # Build publish time
    publish_time = metadata.get('publish_time') or datetime.now(timezone.utc)

    # Normalize URL
    canonical_url = normalize_url(url)

    # Create captured page
    capture = CapturedPage(
        source_url=url,
        canonical_url=canonical_url,
        final_url=final_url,
        status_code=status_code,
        headers={'crawler': 'weixin', 'content-type': 'text/html; charset=UTF-8'},
        fetch_mode=FetchMode.http,
        fetched_at=datetime.now(timezone.utc),
        body=html,
    )

    # Build metadata summary
    meta_lines = []
    if metadata.get('read_count'):
        meta_lines.append(f"Views: {metadata['read_count']:,}")
    if metadata.get('like_count'):
        meta_lines.append(f"Likes: {metadata['like_count']:,}")
    if metadata.get('comment_count'):
        meta_lines.append(f"Comments: {metadata['comment_count']:,}")

    meta_summary = " | ".join(meta_lines) if meta_lines else ""

    # Create workflow
    workflow = _workflow()

    # Create feed entry
    feed = FeedEntry(
        source_url=url,
        canonical_url=canonical_url,
        workflow_id=workflow.id,
        content_type=workflow.meta.content_type,
        title=title,
        author=author,
        published_at=publish_time,
        body=content_text[:500],  # Preview
        comments=comments,
        metadata={
            'crawler': 'weixin',
            'read_count': metadata.get('read_count'),
            'like_count': metadata.get('like_count'),
            'comment_count': metadata.get('comment_count'),
            'publish_timestamp': metadata.get('publish_timestamp'),
            'meta_summary': meta_summary,
        },
        fetched_at=capture.fetched_at,
    )
    feed.compute_content_hash()

    return CrawlerProduct(workflow=workflow, capture=capture, feed=feed)


# Crawler definition
CRAWLER = CrawlerDefinition(
    id="weixin",
    title="WeChat Official Account",
    domains=["mp.weixin.qq.com"],
    url_patterns=[r"https?://mp\.weixin\.qq\.com/s/"],
    handler=crawl,
)
