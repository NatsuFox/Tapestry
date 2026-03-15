"""Weibo public-post crawler definition."""

from _src.models import (
    AnalysisHandoff,
    WorkflowFetch,
    WorkflowKnowledgeBase,
    WorkflowMatch,
    WorkflowMeta,
    WorkflowParse,
    WorkflowProfile,
)
from _src.registry import CrawlerDefinition

CRAWLER = CrawlerDefinition(
    id="weibo",
    title="Weibo",
    domains=["weibo.com", "www.weibo.com", "m.weibo.cn"],
    url_patterns=[
        r"^https?://(?:www\.)?weibo\.com/(?:u/\d+/)?[A-Za-z0-9]+",
        r"^https?://m\.weibo\.cn/detail/\d+",
        r"^https?://m\.weibo\.cn/status/[A-Za-z0-9]+",
    ],
    workflow=WorkflowProfile(
        id="weibo_post",
        meta=WorkflowMeta(
            title="Weibo Post",
            description="Crawler for public Weibo post/detail pages.",
            content_type="discussion",
        ),
        match=WorkflowMatch(
            domains=["weibo.com", "www.weibo.com", "m.weibo.cn"],
            url_patterns=[
                r"^https?://(?:www\.)?weibo\.com/(?:u/\d+/)?[A-Za-z0-9]+",
                r"^https?://m\.weibo\.cn/detail/\d+",
                r"^https?://m\.weibo\.cn/status/[A-Za-z0-9]+",
            ],
        ),
        fetch=WorkflowFetch(mode="http", fallback="browser"),
        parse=WorkflowParse(
            title="meta[property='og:title']@content",
            author="meta[name='author']@content",
            body="meta[property='og:description']@content",
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Summarize the Weibo post and retain the post text, public framing, and any visible discussion signals.",
            instructions=(
                "Use the public Weibo page as the factual source.\n"
                "Preserve the original post wording when it carries the main meaning, and distinguish post content from surrounding platform framing."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="social-weibo"),
    ),
)
