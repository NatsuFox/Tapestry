from pathlib import Path

from _src.models import AnalysisHandoff, CapturedPage, FetchMode, WorkflowKnowledgeBase, WorkflowMatch, WorkflowMeta, WorkflowParse, WorkflowProfile
from _src.parse import Parser


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_article_with_selectors():
    html = (FIXTURES / "sample_article.html").read_text(encoding="utf-8")
    workflow = WorkflowProfile(
        id="article",
        meta=WorkflowMeta(title="Article Workflow"),
        match=WorkflowMatch(),
        parse=WorkflowParse(
            title="h1",
            author=".author",
            published_at="time[datetime]@datetime",
            body=".content",
        ),
        analysis=AnalysisHandoff(),
        kb=WorkflowKnowledgeBase(),
    )
    capture = CapturedPage(
        source_url="https://example.com/article",
        canonical_url="https://example.com/article",
        final_url="https://example.com/article",
        status_code=200,
        fetch_mode=FetchMode.http,
        body=html,
    )
    parser = Parser()
    feed = parser.parse(capture, workflow)
    assert feed.title == "Test Article Title"
    assert feed.author == "Jane Doe"
    assert feed.published_at is not None
    assert "main body of the sample article" in feed.body
    assert feed.content_hash


def test_parse_readability_fallback():
    html = (FIXTURES / "sample_article.html").read_text(encoding="utf-8")
    workflow = WorkflowProfile(
        id="fallback",
        meta=WorkflowMeta(title="Fallback Workflow"),
        parse=WorkflowParse(),
        analysis=AnalysisHandoff(),
        kb=WorkflowKnowledgeBase(),
    )
    capture = CapturedPage(
        source_url="https://example.com/article",
        canonical_url="https://example.com/article",
        final_url="https://example.com/article",
        status_code=200,
        fetch_mode=FetchMode.http,
        body=html,
    )
    feed = Parser().parse(capture, workflow)
    assert feed.title or feed.body


def test_parse_metadata_description_fallback():
    html = """
    <html>
      <head>
        <meta property="og:title" content="Platform Post Title" />
        <meta property="og:description" content="Short post body from metadata." />
        <meta name="author" content="Platform Author" />
      </head>
      <body></body>
    </html>
    """
    workflow = WorkflowProfile(
        id="metadata",
        meta=WorkflowMeta(title="Metadata Workflow"),
        parse=WorkflowParse(),
        analysis=AnalysisHandoff(),
        kb=WorkflowKnowledgeBase(),
    )
    capture = CapturedPage(
        source_url="https://example.com/post",
        canonical_url="https://example.com/post",
        final_url="https://example.com/post",
        status_code=200,
        fetch_mode=FetchMode.http,
        body=html,
    )
    feed = Parser().parse(capture, workflow)
    assert feed.title == "Platform Post Title"
    assert feed.author == "Platform Author"
    assert feed.body == "Short post body from metadata."


def test_parse_discussion_comments():
    html = (FIXTURES / "sample_discussion.html").read_text(encoding="utf-8")
    workflow = WorkflowProfile(
        id="discussion",
        meta=WorkflowMeta(title="Discussion Workflow", content_type="discussion"),
        parse=WorkflowParse(
            title=".title",
            author=".post-author",
            body=".post-body",
            comments={
                "container": ".comment",
                "author": ".comment-author",
                "text": ".comment-text",
                "max_count": 10,
            },
        ),
        analysis=AnalysisHandoff(),
        kb=WorkflowKnowledgeBase(),
    )
    capture = CapturedPage(
        source_url="https://forum.example.com/thread/1",
        canonical_url="https://forum.example.com/thread/1",
        final_url="https://forum.example.com/thread/1",
        status_code=200,
        fetch_mode=FetchMode.http,
        body=html,
    )
    feed = Parser().parse(capture, workflow)
    assert feed.title == "Should we use Rust or Go for our new service?"
    assert len(feed.comments) == 3
    assert feed.comments[0].author == "bob"
    assert "Go is simpler" in feed.comments[0].text
