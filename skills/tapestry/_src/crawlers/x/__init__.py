"""X / Twitter public-post crawler definition."""

from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlencode

import httpx
from selectolax.parser import HTMLParser

from _src.models import (
    AnalysisHandoff,
    CapturedPage,
    FeedEntry,
    FetchMode,
    WorkflowKnowledgeBase,
    WorkflowMatch,
    WorkflowMeta,
    WorkflowProfile,
)
from _src.registry import CrawlerDefinition, CrawlerProduct
from _src.router import normalize_url


def _extract_tweet_id(url: str) -> str:
    parts = url.rstrip("/").split("/")
    if "status" in parts:
        idx = parts.index("status")
        if idx + 1 < len(parts):
            return parts[idx + 1].split("?")[0]
    raise ValueError(f"Unable to extract tweet id from URL: {url}")


def _parse_embed_html(raw_html: str) -> tuple[str, str | None]:
    if not raw_html:
        return "", None
    normalized = raw_html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    tree = HTMLParser(normalized)
    text_node = tree.css_first("p")
    body = text_node.text(separator="\n", strip=True) if text_node else ""
    timestamp_node = tree.css("a")
    timestamp = timestamp_node[-1].text(strip=True) if timestamp_node else None
    return unescape(body.strip()), timestamp


def _parse_timestamp(label: str | None) -> datetime | None:
    if not label:
        return None
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(label, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


async def crawl(
    url: str,
    target_root: Path,
    crawler: CrawlerDefinition,
    fetcher,
    parser,
) -> CrawlerProduct:
    tweet_id = _extract_tweet_id(url)
    oembed_url = f"https://publish.twitter.com/oembed?{urlencode({'url': url, 'omit_script': 'true'})}"
    async with httpx.AsyncClient(
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (compatible; Tapestry/0.1; +https://example.com/bot)"},
        follow_redirects=True,
    ) as client:
        response = await client.get(oembed_url)
        response.raise_for_status()
        payload = response.json()

    body, timestamp_label = _parse_embed_html(payload.get("html", ""))
    author_name = payload.get("author_name") or None
    final_url = payload.get("url") or url
    canonical_url = normalize_url(final_url)

    workflow = crawler.workflow
    if workflow is None:
        raise LookupError("X crawler is missing its workflow definition.")

    capture = CapturedPage(
        source_url=url,
        canonical_url=canonical_url,
        final_url=final_url,
        status_code=response.status_code,
        headers={"content-type": "application/json", "crawler": "x-oembed"},
        fetch_mode=FetchMode.http,
        body=response.text,
    )
    feed = FeedEntry(
        source_url=url,
        canonical_url=canonical_url,
        workflow_id=workflow.id,
        content_type=workflow.meta.content_type,
        title=f"X post by {author_name}" if author_name else f"X post {tweet_id}",
        author=author_name,
        published_at=_parse_timestamp(timestamp_label),
        body=body,
        metadata={
            "crawler": "x",
            "tweet_id": tweet_id,
            "oembed": payload,
            "published_label": timestamp_label,
        },
        fetched_at=capture.fetched_at,
    )
    feed.compute_content_hash()
    return CrawlerProduct(workflow=workflow, capture=capture, feed=feed)


CRAWLER = CrawlerDefinition(
    id="x",
    title="X",
    domains=["x.com", "twitter.com"],
    url_patterns=[
        r"^https?://(?:www\.)?(?:x|twitter)\.com/[^/]+/status/\d+",
        r"^https?://(?:www\.)?(?:x|twitter)\.com/i/status/\d+",
    ],
    workflow=WorkflowProfile(
        id="x_post",
        meta=WorkflowMeta(
            title="X Post",
            description="Crawler for public X / Twitter post pages.",
            content_type="discussion",
        ),
        match=WorkflowMatch(
            domains=["x.com", "twitter.com"],
            url_patterns=[
                r"^https?://(?:www\.)?(?:x|twitter)\.com/[^/]+/status/\d+",
                r"^https?://(?:www\.)?(?:x|twitter)\.com/i/status/\d+",
            ],
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Summarize the public X post, its core claim, and any visible context worth preserving.",
            instructions=(
                "Use the captured X post as the factual source.\n"
                "Preserve the post text, author, timestamp label, and any referenced links or media hints from the embed."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="social-x"),
    ),
    handler=crawl,
)
