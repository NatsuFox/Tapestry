"""Turn captured HTML into a structured feed entry."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from _src.models import CapturedPage, FeedComment, FeedEntry, WorkflowProfile

logger = logging.getLogger(__name__)

_ATTR_RE = re.compile(r"^(.+?)@(\w+)$")


def _select_text(tree: HTMLParser, selector: str) -> str:
    if not selector:
        return ""
    attr_match = _ATTR_RE.match(selector)
    if attr_match:
        css_selector, attr_name = attr_match.groups()
        node = tree.css_first(css_selector)
        return node.attributes.get(attr_name, "") if node else ""
    node = tree.css_first(selector)
    return node.text(strip=True) if node else ""


def _extract_comments(tree: HTMLParser, selector: str, author: str, text: str, max_count: int) -> list[FeedComment]:
    comments: list[FeedComment] = []
    if not selector:
        return comments
    for node in tree.css(selector)[:max_count]:
        sub_tree = HTMLParser(node.html or "")
        comment_text = _select_text(sub_tree, text) if text else node.text(strip=True)
        if not comment_text:
            continue
        comments.append(
            FeedComment(
                author=_select_text(sub_tree, author) or None if author else None,
                text=comment_text,
            )
        )
    return comments


def _extract_metadata(tree: HTMLParser) -> dict:
    import json

    metadata: dict = {}
    for tag in tree.css("meta[property^='og:']"):
        prop = tag.attributes.get("property", "")
        content = tag.attributes.get("content", "")
        if prop and content:
            metadata[prop] = content
    for tag in tree.css("meta[name]"):
        name = tag.attributes.get("name", "")
        content = tag.attributes.get("content", "")
        if name and content:
            metadata[name] = content
    for script in tree.css("script[type='application/ld+json']"):
        try:
            payload = json.loads(script.text())
        except (TypeError, ValueError):
            continue
        if isinstance(payload, dict):
            metadata["json_ld"] = payload
            break
    return metadata


def _readability_fallback(html: str) -> tuple[str, str]:
    try:
        from readability import Document

        document = Document(html)
        title = document.short_title() or ""
        body_tree = HTMLParser(document.summary() or "")
        body = body_tree.body.text(strip=True) if body_tree.body else ""
        return title, body
    except Exception:
        logger.warning("Readability fallback failed")
        return "", ""


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None


class Parser:
    """Apply a workflow profile to captured content and build a feed entry."""

    def parse(self, capture: CapturedPage, workflow: WorkflowProfile) -> FeedEntry:
        rules = workflow.parse
        tree = HTMLParser(capture.body)

        title = _select_text(tree, rules.title)
        author = _select_text(tree, rules.author) or None
        published_raw = _select_text(tree, rules.published_at)
        body = _select_text(tree, rules.body)
        if not title and not body:
            title, body = _readability_fallback(capture.body)

        comments: list[FeedComment] = []
        if rules.comments:
            comments = _extract_comments(
                tree,
                rules.comments.container,
                rules.comments.author,
                rules.comments.text,
                rules.comments.max_count,
            )

        metadata = _extract_metadata(tree)
        if not title:
            title = metadata.get("og:title", "") or metadata.get("twitter:title", "")
        if not author:
            author = metadata.get("author") or None
            raw_author = metadata.get("json_ld", {}).get("author")
            if isinstance(raw_author, dict):
                author = raw_author.get("name") or None
            elif raw_author:
                author = str(raw_author)
        if not body:
            raw_description = (
                metadata.get("og:description")
                or metadata.get("twitter:description")
                or metadata.get("description")
                or metadata.get("json_ld", {}).get("description", "")
            )
            body = str(raw_description or "").strip()

        feed = FeedEntry(
            source_url=capture.source_url,
            canonical_url=capture.canonical_url,
            workflow_id=workflow.id,
            content_type=workflow.meta.content_type,
            title=title,
            author=author,
            published_at=_parse_datetime(published_raw),
            body=body,
            comments=comments,
            metadata=metadata,
            fetched_at=capture.fetched_at,
        )
        feed.compute_content_hash()
        return feed
