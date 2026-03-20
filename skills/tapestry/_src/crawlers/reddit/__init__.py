"""Reddit thread crawler definition."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

from _src.models import (
    AnalysisHandoff,
    CapturedPage,
    FeedComment,
    FeedEntry,
    FetchMode,
    WorkflowKnowledgeBase,
    WorkflowMatch,
    WorkflowMeta,
    WorkflowProfile,
)
from _src.registry import CrawlerDefinition, CrawlerProduct
from _src.router import normalize_url


def _api_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    return f"https://api.reddit.com{path}.json?raw_json=1"


def _flatten_comments(nodes, comments: list[FeedComment]) -> None:
    for node in nodes or []:
        if not isinstance(node, dict) or node.get("kind") != "t1":
            continue
        data = node.get("data") or {}
        body = (data.get("body") or "").strip()
        author = data.get("author") or None
        if body:
            comments.append(FeedComment(author=author, text=body))
        replies = data.get("replies")
        if isinstance(replies, dict):
            _flatten_comments((replies.get("data") or {}).get("children") or [], comments)


async def crawl(
    url: str,
    target_root: Path,
    crawler: CrawlerDefinition,
    fetcher,
    parser,
) -> CrawlerProduct:
    api_url = _api_url(url)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Tapestry/0.1; +https://example.com/bot)"}
    async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
        response = await client.get(api_url)
        response.raise_for_status()
        payload = response.json()

    post = payload[0]["data"]["children"][0]["data"]
    comment_nodes = payload[1]["data"]["children"]
    comments: list[FeedComment] = []
    _flatten_comments(comment_nodes, comments)

    title = post.get("title") or "Reddit thread"
    body_parts = [title]
    if post.get("selftext"):
        body_parts.append(post["selftext"])
    if post.get("url_overridden_by_dest"):
        body_parts.append(f"Linked media: {post['url_overridden_by_dest']}")
    body = "\n\n".join(part for part in body_parts if part).strip()

    workflow = crawler.workflow
    if workflow is None:
        raise LookupError("Reddit crawler is missing its workflow definition.")

    final_url = f"https://www.reddit.com{post.get('permalink')}" if post.get("permalink") else url
    canonical_url = normalize_url(final_url)
    published = (
        datetime.fromtimestamp(post.get("created_utc") or 0, tz=timezone.utc) if post.get("created_utc") else None
    )

    capture = CapturedPage(
        source_url=url,
        canonical_url=canonical_url,
        final_url=final_url,
        status_code=response.status_code,
        headers={"content-type": "application/json", "crawler": "reddit-api"},
        fetch_mode=FetchMode.http,
        body=response.text,
    )
    feed = FeedEntry(
        source_url=url,
        canonical_url=canonical_url,
        workflow_id=workflow.id,
        content_type=workflow.meta.content_type,
        title=title,
        author=post.get("author") or None,
        published_at=published,
        body=body,
        comments=comments,
        metadata={
            "crawler": "reddit",
            "score": post.get("score"),
            "num_comments": post.get("num_comments"),
            "subreddit": post.get("subreddit"),
            "post_hint": post.get("post_hint"),
        },
        fetched_at=capture.fetched_at,
    )
    feed.compute_content_hash()
    return CrawlerProduct(workflow=workflow, capture=capture, feed=feed)


CRAWLER = CrawlerDefinition(
    id="reddit",
    title="Reddit",
    domains=["reddit.com", "old.reddit.com", "api.reddit.com", "sh.reddit.com"],
    url_patterns=[r"^https?://([^/]+\.)?reddit\.com/r/[^/]+/comments/"],
    workflow=WorkflowProfile(
        id="reddit_thread",
        meta=WorkflowMeta(
            title="Reddit Thread",
            description="Crawler for Reddit comment threads.",
            content_type="discussion",
        ),
        match=WorkflowMatch(
            domains=["reddit.com", "old.reddit.com", "api.reddit.com", "sh.reddit.com"],
            url_patterns=[r"^https?://([^/]+\.)?reddit\.com/r/[^/]+/comments/"],
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Produce a thread synthesis that preserves the original post and the strongest discussion signals.",
            instructions=(
                "Start from the Reddit post title, body, linked media URL, and flattened comments.\n"
                "Capture the original thesis, main reply positions, and any concrete evidence or examples."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="community-discussions"),
    ),
    handler=crawl,
)
