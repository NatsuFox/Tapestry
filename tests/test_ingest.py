import json
from pathlib import Path

import _src.store as store_module
import pytest
from _src.config import TapestryConfig
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


def _article_fetcher() -> StaticFetcher:
    return StaticFetcher((FIXTURES / "sample_article.html").read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_ingest_text_creates_capture_feed_and_note(tmp_path):
    store = KnowledgeBaseStore(tmp_path)
    service = IngestionService(
        registry=CrawlerRegistry(),
        store=store,
        fetcher=_article_fetcher(),
    )

    report = await service.ingest_text("Please ingest https://example.com/articles/test for the knowledge base.")

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
    assert "_data/notes" in result.note_path
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
        fetcher=_article_fetcher(),
    )

    first = await service.ingest_urls(["https://example.com/articles/test"])
    second = await service.ingest_urls(["https://example.com/articles/test"])

    assert first.results[0].status == "stored"
    assert second.results[0].status == "duplicate"
    assert first.results[0].note_path == second.results[0].note_path
    assert second.results[0].analysis.skill == "tapestry-synthesis"


def test_store_without_explicit_config_uses_project_local_data_dir(tmp_path, monkeypatch):
    shared_skill_root = tmp_path.parent / "shared-skill"
    shared_data_root = shared_skill_root / "_data"
    config = TapestryConfig.model_validate(
        {
            "paths": {
                "project_root": str(shared_skill_root),
                "data_dir": str(shared_data_root),
            }
        }
    )
    monkeypatch.setattr(
        store_module.TapestryConfig,
        "load",
        classmethod(lambda cls, config_path=None: config),
    )

    store = KnowledgeBaseStore(tmp_path)

    assert store.data_root == (tmp_path / "_data").resolve()


@pytest.mark.asyncio
async def test_store_load_handoff_returns_structured_context(tmp_path):
    store = KnowledgeBaseStore(tmp_path)
    service = IngestionService(
        registry=CrawlerRegistry(),
        store=store,
        fetcher=_article_fetcher(),
    )

    report = await service.ingest_urls(["https://example.com/articles/test"])
    handoff = store.load_handoff(note_path=report.results[0].note_path)

    assert handoff["analysis"]["skill"] == "tapestry-synthesis"
    assert handoff["feed_payload"]["title"] == "Test Article Title"
    assert handoff["analysis"]["instructions"] != ""


@pytest.mark.asyncio
async def test_store_load_handoff_accepts_absolute_note_path(tmp_path):
    shared_data_root = tmp_path.parent / "shared-data"
    config = TapestryConfig.model_validate(
        {
            "paths": {
                "project_root": str(tmp_path),
                "data_dir": str(shared_data_root),
            }
        }
    )
    store = KnowledgeBaseStore(tmp_path, config=config)
    service = IngestionService(
        registry=CrawlerRegistry(),
        store=store,
        fetcher=_article_fetcher(),
    )

    report = await service.ingest_urls(["https://example.com/articles/test"])
    note_path = report.results[0].note_path

    assert Path(note_path).is_absolute()
    handoff = store.load_handoff(note_path=note_path)

    assert handoff["analysis"]["skill"] == "tapestry-synthesis"
    assert handoff["feed_payload"]["title"] == "Test Article Title"
