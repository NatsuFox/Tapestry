"""Generic HTML crawler definition."""

from _src.models import (
    AnalysisHandoff,
    FetchMode,
    WorkflowFetch,
    WorkflowKnowledgeBase,
    WorkflowMeta,
    WorkflowParse,
    WorkflowProfile,
)
from _src.registry import CrawlerDefinition

CRAWLER = CrawlerDefinition(
    id="generic_html",
    title="Generic HTML",
    workflow=WorkflowProfile(
        id="generic_html",
        meta=WorkflowMeta(
            title="Generic HTML",
            description="Fallback crawler for article-like HTML pages with browser rendering support.",
            content_type="article",
        ),
        fetch=WorkflowFetch(
            mode=FetchMode.http,
            fallback=FetchMode.browser,
        ),
        parse=WorkflowParse(
            title="h1, .title, [class*='title'], [id*='title']",
            body="article, main, .content, [role='main'], .main-content, #content",
        ),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Create a well-organized synthesis note from the article.",
            instructions=(
                "Focus on the article's main thesis, key arguments, and concrete claims. "
                "Preserve technical details and important context."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="web-clippings"),
    ),
)
