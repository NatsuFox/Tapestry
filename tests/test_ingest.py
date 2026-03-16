import json
from pathlib import Path

import pytest

from _src.ingest import IngestionService
from _src.models import CapturedPage, FetchMode
from _src.registry import CrawlerRegistry
from _src.store import KnowledgeBaseStore


FIXTURES = Path(__file__).parent / "fixtures"


class StaticFetcher:
    def __init__(self, html: str) -> None:
        self._html = html

    async def fetch(self, url, fetch_cfg):
        return CapturedPage(
            source_url=url,
            canonical_url=url,
            final_url=url,
            status_code=200,
            fetch_mode=FetchMode.http,
            body=self._html,
        )


@pytest.mark.asyncio
async def test_ingest_text_creates_capture_feed_and_note(tmp_path):
    store = KnowledgeBaseStore(tmp_path)
    service = IngestionService(
        registry=CrawlerRegistry(),
        store=store,
        fetcher=StaticFetcher((FIXTURES / "sample_article.html").read_text(encoding="utf-8")),
    )

    report = await service.ingest_text(
        "Please ingest https://example.com/articles/test for the knowledge base."
    )

    assert report.stored_count == 1
    result = report.results[0]
    assert result.status == "stored"

    capture_path = tmp_path / result.capture_path
    feed_path = tmp_path / result.feed_path
    note_path = tmp_path / result.note_path

    assert capture_path.exists()
    assert feed_path.exists()
    assert note_path.exists()

    feed_payload = json.loads(feed_path.read_text(encoding="utf-8"))
    assert feed_payload["title"] == "Test Article Title"
    assert "knowledge-base" in result.note_path
    assert result.analysis.skill == "tapestry-synthesis"
    note_text = note_path.read_text(encoding="utf-8")
    assert "## Deterministic Highlights" in note_text
    assert "## Analysis Handoff" in note_text
    assert "Test Article Title" in note_text


@pytest.mark.asyncio
async def test_ingest_reuses_existing_note_for_duplicates(tmp_path):
    store = KnowledgeBaseStore(tmp_path)
    service = IngestionService(
        registry=CrawlerRegistry(),
        store=store,
        fetcher=StaticFetcher((FIXTURES / "sample_article.html").read_text(encoding="utf-8")),
    )

    first = await service.ingest_urls(["https://example.com/articles/test"])
    second = await service.ingest_urls(["https://example.com/articles/test"])

    assert first.results[0].status == "stored"
    assert second.results[0].status == "duplicate"
    assert first.results[0].note_path == second.results[0].note_path
    assert second.results[0].analysis.skill == "tapestry-synthesis"


@pytest.mark.asyncio
async def test_store_load_handoff_returns_structured_context(tmp_path):
    store = KnowledgeBaseStore(tmp_path)
    service = IngestionService(
        registry=CrawlerRegistry(),
        store=store,
        fetcher=StaticFetcher((FIXTURES / "sample_article.html").read_text(encoding="utf-8")),
    )

    report = await service.ingest_urls(["https://example.com/articles/test"])
    handoff = store.load_handoff(note_path=report.results[0].note_path)

    assert handoff["analysis"]["skill"] == "tapestry-synthesis"
    assert handoff["feed_payload"]["title"] == "Test Article Title"
    assert "Read the stored note" in handoff["analysis"]["instructions"]
