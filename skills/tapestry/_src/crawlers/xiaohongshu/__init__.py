"""Xiaohongshu public note/profile crawler definition."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

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


def _extract_state(html: str) -> str | None:
    marker = "window.__INITIAL_STATE__="
    start = html.find(marker)
    if start < 0:
        return None
    index = start + len(marker)
    while index < len(html) and html[index] != "{":
        index += 1
    depth = 0
    in_string = False
    quote = ""
    escape = False
    for pos in range(index, len(html)):
        ch = html[pos]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_string = False
        else:
            if ch in ('"', "'"):
                in_string = True
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return html[index : pos + 1]
    return None


def _state_to_json(raw: str) -> dict:
    normalized = re.sub(r":\s*undefined(?=[,}])", ": null", raw)
    normalized = re.sub(r"\bundefined\b", "null", normalized)
    return json.loads(normalized)


def _profile_body(profile_data: dict) -> str:
    basic = profile_data.get("basicInfo") or {}
    interactions = profile_data.get("interactions") or []
    notes = ((profile_data.get("notes") or [[]])[0] or [])[:5]
    lines = []
    if basic.get("desc"):
        lines.append(str(basic["desc"]).strip())
    for item in interactions:
        if not isinstance(item, dict):
            continue
        if item.get("name") and item.get("count") is not None:
            lines.append(f"{item['name']}: {item['count']}")
    note_titles = []
    for note in notes:
        card = (note or {}).get("noteCard") or {}
        title = (card.get("displayTitle") or card.get("title") or "").strip()
        if title:
            note_titles.append(title)
    if note_titles:
        lines.append("Recent notes:")
        lines.extend(f"- {title}" for title in note_titles)
    return "\n".join(lines).strip()


def _meta_content(html: str, key: str) -> str:
    tree = HTMLParser(html)
    node = tree.css_first(f"meta[property='{key}'], meta[name='{key}']")
    if not node:
        return ""
    return unescape((node.attributes.get("content") or "").strip())


def _document_title(html: str) -> str:
    tree = HTMLParser(html)
    node = tree.css_first("title")
    return unescape(node.text(strip=True) if node else "")


def _note_body(note: dict) -> str:
    parts = [note.get("title") or "", note.get("desc") or ""]
    tags = note.get("tagList") or []
    if tags:
        parts.append("Tags: " + ", ".join(tag.get("name", "") for tag in tags if tag.get("name")))
    return "\n\n".join(part.strip() for part in parts if part and str(part).strip())


def _parse_time(ms_value) -> datetime | None:
    if isinstance(ms_value, (int, float)):
        return datetime.fromtimestamp(ms_value / 1000, tz=timezone.utc)
    return None


async def crawl(
    url: str,
    target_root: Path,
    crawler: CrawlerDefinition,
    fetcher,
    parser,
) -> CrawlerProduct:
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    raw_state = _extract_state(html)
    if not raw_state:
        raise RuntimeError("Xiaohongshu page did not expose window.__INITIAL_STATE__.")
    state = _state_to_json(raw_state)
    final_url = response.url.__str__()
    is_profile_url = "/user/profile/" in final_url

    note_map = (((state.get("note") or {}).get("noteDetailMap")) or {})
    if note_map and not is_profile_url:
        note_detail = next(iter(note_map.values()))
        note = note_detail.get("note") or {}
        workflow = WorkflowProfile(
            id="xiaohongshu_note",
            meta=WorkflowMeta(
                title="Xiaohongshu Note",
                description="Crawler for public Xiaohongshu note pages.",
                content_type="article",
            ),
            match=WorkflowMatch(
                domains=["xiaohongshu.com", "www.xiaohongshu.com", "xhslink.com"],
                url_patterns=[
                    r"^https?://(?:www\.)?xiaohongshu\.com/explore/[A-Za-z0-9]+",
                    r"^https?://(?:www\.)?xiaohongshu\.com/discovery/item/[A-Za-z0-9]+",
                    r"^https?://(?:www\.)?xhslink\.com/[A-Za-z0-9]+",
                ],
            ),
            analysis=AnalysisHandoff(
                skill="tapestry-synthesis",
                deliverable="Summarize the Xiaohongshu note and preserve the strongest concrete tips, claims, or examples.",
                instructions=(
                    "Ground the synthesis in the note title, description, tags, author, and visible interaction metadata.\n"
                    "Separate platform framing from specific reusable claims or recommendations."
                ),
            ),
            kb=WorkflowKnowledgeBase(collection="social-xiaohongshu"),
        )
        title = (note.get("title") or "").strip() or "Xiaohongshu Note"
        author = ((note.get("user") or {}).get("nickname") or None)
        body = _note_body(note)
        metadata = {"crawler": "xiaohongshu", "state": note_detail}
        published = _parse_time(note.get("time") or note.get("lastUpdateTime"))
    else:
        user_page = ((state.get("user") or {}).get("userPageData")) or {}
        basic = user_page.get("basicInfo") or {}
        workflow = WorkflowProfile(
            id="xiaohongshu_profile",
            meta=WorkflowMeta(
                title="Xiaohongshu Profile",
                description="Crawler for public Xiaohongshu profile pages.",
                content_type="profile",
            ),
            match=WorkflowMatch(
                domains=["xiaohongshu.com", "www.xiaohongshu.com"],
                url_patterns=[r"^https?://(?:www\.)?xiaohongshu\.com/user/profile/[A-Za-z0-9]+$"],
            ),
            analysis=AnalysisHandoff(
                skill="tapestry-synthesis",
                deliverable="Summarize the Xiaohongshu author profile and preserve the most relevant profile signals.",
                instructions=(
                    "Ground the summary in the profile bio, visible interaction counts, and surfaced recent-note titles.\n"
                    "Prioritize stable profile information over marketing copy."
                ),
            ),
            kb=WorkflowKnowledgeBase(collection="social-xiaohongshu"),
        )
        title = (basic.get("nickname") or "").strip() or "Xiaohongshu Profile"
        author = basic.get("nickname") or None
        body = _profile_body(user_page)
        if not body:
            body = (
                _meta_content(html, "og:description")
                or _meta_content(html, "description")
                or _document_title(html)
            )
        if title == "Xiaohongshu Profile":
            title = _meta_content(html, "og:title") or _document_title(html) or title
        if not author:
            author = title.removesuffix(" - 小红书").strip() or None
        metadata = {"crawler": "xiaohongshu", "state": user_page}
        published = None

    canonical_url = normalize_url(final_url)
    capture = CapturedPage(
        source_url=url,
        canonical_url=canonical_url,
        final_url=final_url,
        status_code=response.status_code,
        headers={"content-type": "text/html", "crawler": "xiaohongshu-state"},
        fetch_mode=FetchMode.http,
        body=html,
    )
    feed = FeedEntry(
        source_url=url,
        canonical_url=canonical_url,
        workflow_id=workflow.id,
        content_type=workflow.meta.content_type,
        title=title,
        author=author,
        published_at=published,
        body=body,
        metadata=metadata,
        fetched_at=capture.fetched_at,
    )
    feed.compute_content_hash()
    return CrawlerProduct(workflow=workflow, capture=capture, feed=feed)


CRAWLER = CrawlerDefinition(
    id="xiaohongshu",
    title="Xiaohongshu",
    domains=["xiaohongshu.com", "www.xiaohongshu.com", "xhslink.com"],
    url_patterns=[
        r"^https?://(?:www\.)?xiaohongshu\.com/explore/[A-Za-z0-9]+",
        r"^https?://(?:www\.)?xiaohongshu\.com/discovery/item/[A-Za-z0-9]+",
        r"^https?://(?:www\.)?xiaohongshu\.com/user/profile/[A-Za-z0-9]+$",
        r"^https?://(?:www\.)?xhslink\.com/[A-Za-z0-9]+",
    ],
    handler=crawl,
)
