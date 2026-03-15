"""Hacker News discussion crawler definition."""

from _src.models import (
    AnalysisHandoff,
    CommentRule,
    WorkflowKnowledgeBase,
    WorkflowMatch,
    WorkflowMeta,
    WorkflowParse,
    WorkflowProfile,
)
from _src.registry import CrawlerDefinition

CRAWLER = CrawlerDefinition(
    id="hackernews",
    title="Hacker News",
    domains=["news.ycombinator.com"],
    url_patterns=[r"^https?://news\.ycombinator\.com/item\?id="],
    workflow=WorkflowProfile(
        id="hackernews_discussion",
        meta=WorkflowMeta(
            title="Hacker News Discussion",
            description="Crawler for Hacker News item pages.",
            content_type="discussion",
        ),
        match=WorkflowMatch(
            domains=["news.ycombinator.com"],
            url_patterns=[r"^https?://news\.ycombinator\.com/item\?id="],
        ),
        parse=WorkflowParse(
            title=".titleline > a",
            author=".hnuser",
            published_at=".age@title",
            body=".toptext",
            comments=CommentRule(
                container=".comtr",
                author=".hnuser",
                text=".commtext",
                max_count=40,
            ),
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Produce a discussion synthesis that captures the story, argument threads, and corrections.",
            instructions=(
                "Use the stored discussion note as the factual base layer.\n"
                "Identify the linked story, dominant viewpoints, and any corrections or caveats that materially change the interpretation."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="tech-discussions"),
    ),
)
