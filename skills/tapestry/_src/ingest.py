"""End-to-end orchestration from URL to feed to knowledge-base note."""

from __future__ import annotations

from pathlib import Path

from _src.fetch import Fetcher
from _src.links import extract_urls
from _src.models import BatchIngestReport, CatalogRecord, IngestResult
from _src.parse import Parser
from _src.registry import CrawlerRegistry
from _src.store import KnowledgeBaseStore


class IngestionService:
    """Turn URLs into captures, feed entries, and knowledge-base notes."""

    def __init__(
        self,
        registry: CrawlerRegistry,
        store: KnowledgeBaseStore,
        fetcher: Fetcher | None = None,
        parser: Parser | None = None,
    ) -> None:
        self._registry = registry
        self._store = store
        self._fetcher = fetcher or Fetcher()
        self._parser = parser or Parser()

    @classmethod
    def for_project_root(
        cls,
        project_root: Path | None = None,
        *,
        registry: CrawlerRegistry | None = None,
    ) -> "IngestionService":
        root = cls._resolve_project_root(project_root)
        store = KnowledgeBaseStore(root)
        return cls(registry=registry or CrawlerRegistry(), store=store)

    @staticmethod
    def _resolve_project_root(project_root: Path | None) -> Path:
        if project_root is not None:
            return Path(project_root).resolve()
        return Path.cwd().resolve()

    async def ingest_text(self, text: str) -> BatchIngestReport:
        urls = extract_urls(text)
        if not urls:
            raise ValueError("No URLs were found in the provided text.")
        return await self.ingest_urls(urls)

    async def ingest_urls(
        self,
        urls: list[str],
        *,
        forced_crawler_id: str | None = None,
    ) -> BatchIngestReport:
        unique_urls = list(dict.fromkeys(urls))
        results: list[IngestResult] = []
        stored_count = 0
        duplicate_count = 0

        for url in unique_urls:
            crawler = (
                self._registry.get(forced_crawler_id)
                if forced_crawler_id
                else self._registry.match(url)
            )
            if crawler is None:
                raise LookupError(f"Requested crawler not found: {forced_crawler_id}")
            if crawler.handler is not None:
                product = await crawler.handler(
                    url,
                    self._store.project_root,
                    crawler,
                    self._fetcher,
                    self._parser,
                )
                workflow = product.workflow
                capture = product.capture
                feed = product.feed
            else:
                workflow = crawler.workflow
                if workflow is None:
                    raise LookupError(f"Crawler {crawler.id} has no workflow or handler.")
                capture = await self._fetcher.fetch(url, workflow.fetch)
                feed = self._parser.parse(capture, workflow)

            capture_path = self._store.save_capture(capture)
            feed.capture_path = capture_path
            feed_path = self._store.save_feed(feed)
            digest = self._store.build_digest(feed, workflow)

            existing = self._store.find_existing(feed.canonical_url, feed.content_hash)
            if existing:
                duplicate_count += 1
                results.append(
                    IngestResult(
                        source_url=url,
                        canonical_url=feed.canonical_url,
                        workflow_id=workflow.id,
                        collection=existing.collection,
                        title=existing.title,
                        status="duplicate",
                        digest=existing.digest,
                        analysis=existing.analysis,
                        capture_path=capture_path,
                        feed_path=feed_path,
                        note_path=existing.note_path,
                    )
                )
                continue

            note_path = self._store.save_note(
                workflow=workflow,
                feed=feed,
                digest=digest,
                capture_path=capture_path,
                feed_path=feed_path,
            )
            self._store.append_catalog(
                CatalogRecord(
                    source_url=url,
                    canonical_url=feed.canonical_url,
                    workflow_id=workflow.id,
                    collection=workflow.kb.collection,
                    title=feed.title,
                    digest=digest,
                    analysis=workflow.analysis,
                    content_hash=feed.content_hash,
                    capture_path=capture_path,
                    feed_path=feed_path,
                    note_path=note_path,
                )
            )
            stored_count += 1
            results.append(
                IngestResult(
                    source_url=url,
                    canonical_url=feed.canonical_url,
                    workflow_id=workflow.id,
                    collection=workflow.kb.collection,
                    title=feed.title,
                    status="stored",
                    digest=digest,
                    analysis=workflow.analysis,
                    capture_path=capture_path,
                    feed_path=feed_path,
                    note_path=note_path,
                )
            )

        return BatchIngestReport(
            requested_urls=unique_urls,
            results=results,
            stored_count=stored_count,
            duplicate_count=duplicate_count,
        )
