"""Zhihu crawler backed by the reverse-engineered browser/API implementation."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

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


def _workflow_for_kind(kind: str) -> WorkflowProfile:
    title_map = {
        "zhuanlan.article": "Zhihu Column Article",
        "question": "Zhihu Question",
        "answer": "Zhihu Answer",
        "profile": "Zhihu Profile",
    }
    content_type_map = {
        "zhuanlan.article": "article",
        "question": "discussion",
        "answer": "discussion",
        "profile": "profile",
    }
    collection_map = {
        "zhuanlan.article": "zhihu-columns",
        "question": "zhihu-discussions",
        "answer": "zhihu-discussions",
        "profile": "zhihu-profiles",
    }
    deliverable_map = {
        "zhuanlan.article": "Write a grounded synthesis of the Zhihu column article.",
        "question": "Summarize the Zhihu question, answer landscape, and comment signals.",
        "answer": "Summarize the Zhihu answer and its surrounding discussion context.",
        "profile": "Summarize the Zhihu author profile and its most relevant signals.",
    }
    return WorkflowProfile(
        id=f"zhihu_{kind.replace('.', '_')}",
        meta=WorkflowMeta(
            title=title_map.get(kind, "Zhihu Page"),
            description="Reverse-engineered Zhihu crawler output.",
            content_type=content_type_map.get(kind, "article"),
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable=deliverable_map.get(kind, "Summarize the Zhihu page using the stored artifacts."),
            instructions=(
                "Use the stored Zhihu artifacts as the factual base layer.\n"
                "Prefer concrete claims, extracted counts, and discussion structure over loose paraphrase."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection=collection_map.get(kind, "zhihu")),
    )


def _body_from_payload(kind: str, payload: dict) -> str:
    parsed = payload.get("parsed") or {}
    fetch = payload.get("fetch") or {}
    content = fetch.get("content") or {}
    text = (content.get("text") or "").strip()
    if kind == "question":
        top_answers = parsed.get("topAnswers") or []
        snippets = [
            answer.get("excerpt", "").strip()
            for answer in top_answers
            if isinstance(answer, dict) and answer.get("excerpt")
        ]
        if snippets:
            return "\n\n".join(snippets)
    if kind == "profile":
        lines = [parsed.get("headline") or "", parsed.get("description") or ""]
        counts = [
            ("Followers", parsed.get("followerCount")),
            ("Following", parsed.get("followingCount")),
            ("Answers", parsed.get("answerCount")),
            ("Articles", parsed.get("articlesCount")),
            ("Pins", parsed.get("pinsCount")),
        ]
        lines.extend(f"{label}: {value}" for label, value in counts if value not in (None, ""))
        body = "\n".join(item for item in lines if item)
        return body.strip()
    if kind == "answer":
        return text or (parsed.get("excerpt") or "").strip()
    if kind == "zhuanlan.article":
        return (text or parsed.get("excerpt") or "").strip()
    return text


def _comments_from_payload(payload: dict) -> list[FeedComment]:
    parsed_comments = ((payload.get("parsed") or {}).get("comments") or {}).get("flatComments") or []
    comments: list[FeedComment] = []
    for item in parsed_comments:
        if not isinstance(item, dict):
            continue
        text = (item.get("contentText") or "").strip()
        if not text:
            continue
        author = ((item.get("author") or {}).get("name") or None)
        comments.append(FeedComment(author=author, text=text))
    return comments


def _parse_timestamp(value) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    return datetime.now(timezone.utc)


async def _run_cli(url: str, project_root: Path) -> dict:
    cli_path = Path(__file__).resolve().parent / "src" / "cli.mjs"
    process = await asyncio.create_subprocess_exec(
        "node",
        str(cli_path),
        "--format",
        "json",
        "--retries",
        "2",
        "--retry-delay-ms",
        "1000",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(project_root),
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError((stderr or stdout).decode("utf-8", errors="replace").strip())
    payload = json.loads(stdout.decode("utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("Zhihu crawler returned no results.")
    return payload[0]


async def crawl(
    url: str,
    target_root: Path,
    crawler: CrawlerDefinition,
    fetcher,
    parser,
) -> CrawlerProduct:
    payload = await _run_cli(url, target_root)
    parsed = payload.get("parsed") or {}
    fetch = payload.get("fetch") or {}
    final_url = fetch.get("finalUrl") or payload.get("url") or url
    canonical_url = normalize_url(final_url)
    kind = parsed.get("kind") or payload.get("detectedKind") or "zhihu"
    workflow = _workflow_for_kind(kind)
    title = parsed.get("title") or parsed.get("questionTitle") or parsed.get("name") or canonical_url
    author = parsed.get("author") or None
    body = _body_from_payload(kind, payload)
    comments = _comments_from_payload(payload)
    created_hint = (
        parsed.get("updatedTime")
        or parsed.get("createdTime")
        or parsed.get("updated")
        or parsed.get("created")
    )

    capture = CapturedPage(
        source_url=url,
        canonical_url=canonical_url,
        final_url=final_url,
        status_code=200,
        headers={"crawler": "zhihu", "content-type": "application/json"},
        fetch_mode=FetchMode.browser,
        fetched_at=_parse_timestamp(created_hint),
        body=json.dumps(payload, ensure_ascii=False),
    )
    feed = FeedEntry(
        source_url=url,
        canonical_url=canonical_url,
        workflow_id=workflow.id,
        content_type=workflow.meta.content_type,
        title=title,
        author=author,
        published_at=_parse_timestamp(created_hint),
        body=body,
        comments=comments,
        metadata={"crawler": "zhihu", "parsed": parsed},
        fetched_at=capture.fetched_at,
    )
    feed.compute_content_hash()
    return CrawlerProduct(workflow=workflow, capture=capture, feed=feed)


CRAWLER = CrawlerDefinition(
    id="zhihu",
    title="Zhihu",
    domains=["zhihu.com", "zhuanlan.zhihu.com"],
    url_patterns=[
        r"^https?://zhuanlan\.zhihu\.com/p/\d+",
        r"^https?://www\.zhihu\.com/question/\d+",
        r"^https?://www\.zhihu\.com/question/\d+/answer/\d+",
        r"^https?://www\.zhihu\.com/people/[^/?#]+",
    ],
    handler=crawl,
)
