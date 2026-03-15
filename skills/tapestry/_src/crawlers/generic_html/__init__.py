"""Generic HTML crawler definition."""

from _src.models import (
    AnalysisHandoff,
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
            description="Fallback crawler for article-like HTML pages.",
            content_type="article",
        ),
        parse=WorkflowParse(),
        analysis=AnalysisHandoff(
            skill="tapestry-synthesis",
            deliverable="Write a concise synthesis or research note grounded in the stored article.",
            instructions=(
                "Read the stored note, feed JSON, and capture JSON before synthesizing.\n"
                "Focus on the article's thesis, strongest concrete claims, and the parts worth preserving for later reuse."
            ),
        ),
        kb=WorkflowKnowledgeBase(collection="web-clippings"),
    ),
)
