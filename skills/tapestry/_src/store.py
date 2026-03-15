"""File-based storage for captures, feeds, and knowledge-base notes."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from _src.models import AnalysisHandoff, CapturedPage, CatalogRecord, FeedEntry, WorkflowProfile


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^\w]+", "-", value.strip().lower(), flags=re.UNICODE).strip("-")
    return normalized[:80] or "entry"


def _url_slug(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}"
    return _slugify(raw)


def _first_excerpt(text: str, limit: int = 240) -> str:
    chunks = [chunk.strip() for chunk in text.splitlines() if chunk.strip()]
    if not chunks:
        return ""
    excerpt = chunks[0]
    if len(excerpt) <= limit:
        return excerpt
    return f"{excerpt[: limit - 3].rstrip()}..."


class KnowledgeBaseStore:
    """Persist each ingest stage to the project tree."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = Path(project_root).resolve()
        self._capture_root = self._project_root / "data" / "captures"
        self._feed_root = self._project_root / "data" / "feeds"
        self._note_root = self._project_root / "knowledge-base" / "notes"
        self._catalog_path = self._project_root / "knowledge-base" / "catalog.jsonl"
        self._ensure_layout()

    def save_capture(self, capture: CapturedPage) -> str:
        base_name = self._timestamped_name(capture.fetched_at, _url_slug(capture.final_url))
        path = self._dated_path(self._capture_root, capture.fetched_at, f"{base_name}.json")
        self._write_json(path, capture.model_dump(mode="json"))
        return self._relative(path)

    def save_feed(self, feed: FeedEntry) -> str:
        slug = _slugify(feed.title) if feed.title else _url_slug(feed.canonical_url)
        base_name = self._timestamped_name(feed.fetched_at, slug)
        path = self._dated_path(self._feed_root, feed.fetched_at, f"{base_name}.json")
        self._write_json(path, feed.model_dump(mode="json"))
        return self._relative(path)

    def save_note(
        self,
        workflow: WorkflowProfile,
        feed: FeedEntry,
        digest: str,
        capture_path: str,
        feed_path: str,
    ) -> str:
        slug = _slugify(feed.title) if feed.title else _url_slug(feed.canonical_url)
        base_name = self._timestamped_name(feed.fetched_at, slug)
        path = self._dated_path(self._note_root, feed.fetched_at, f"{base_name}.md")
        path.write_text(
            self._render_note(
                workflow=workflow,
                feed=feed,
                digest=digest,
                capture_path=capture_path,
                feed_path=feed_path,
            ),
            encoding="utf-8",
        )
        return self._relative(path)

    def append_catalog(self, record: CatalogRecord) -> None:
        self._catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with self._catalog_path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json())
            handle.write("\n")

    def find_existing(self, canonical_url: str, content_hash: str) -> CatalogRecord | None:
        for record in self._iter_catalog_records():
            if record.canonical_url == canonical_url or record.content_hash == content_hash:
                return record
        return None

    def load_handoff(self, *, note_path: str | None = None, url: str | None = None) -> dict:
        if not note_path and not url:
            raise ValueError("Provide either note_path or url to load analysis handoff context.")
        record = (
            self._find_record_by_note_path(note_path) if note_path else self._find_record_by_url(url or "")
        )
        if record is None:
            identifier = note_path or url or "unknown target"
            raise ValueError(f"No stored catalog entry matched: {identifier}")
        note_file = self._project_root / record.note_path
        feed_file = self._project_root / record.feed_path
        capture_file = self._project_root / record.capture_path
        return {
            "title": record.title,
            "canonical_url": record.canonical_url,
            "crawler_id": record.workflow_id,
            "workflow_id": record.workflow_id,
            "collection": record.collection,
            "digest": record.digest,
            "analysis": record.analysis.model_dump(),
            "note_path": record.note_path,
            "feed_path": record.feed_path,
            "capture_path": record.capture_path,
            "note_text": note_file.read_text(encoding="utf-8") if note_file.exists() else "",
            "feed_payload": self._read_json_file(feed_file),
            "capture_payload": self._read_json_file(capture_file),
        }

    def build_digest(self, feed: FeedEntry, workflow: WorkflowProfile) -> str:
        bullets: list[str] = [f"- Crawler: {workflow.meta.title}"]
        if feed.author:
            bullets.append(f"- Author: {feed.author}")
        if feed.published_at:
            bullets.append(f"- Published: {feed.published_at.isoformat()}")
        excerpt = _first_excerpt(feed.body)
        if excerpt:
            bullets.append(f"- Primary excerpt: {excerpt}")
        if feed.comments:
            snapshot = "; ".join(
                _first_excerpt(comment.text, limit=120).replace("\n", " ")
                for comment in feed.comments[:3]
                if comment.text.strip()
            )
            if snapshot:
                bullets.append(f"- Discussion snapshot: {snapshot}")
        return "\n".join(bullets)

    def _ensure_layout(self) -> None:
        self._capture_root.mkdir(parents=True, exist_ok=True)
        self._feed_root.mkdir(parents=True, exist_ok=True)
        self._note_root.mkdir(parents=True, exist_ok=True)
        self._catalog_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def project_root(self) -> Path:
        return self._project_root

    def _relative(self, path: Path) -> str:
        return path.relative_to(self._project_root).as_posix()

    def _iter_catalog_records(self):
        if not self._catalog_path.exists():
            return
        with self._catalog_path.open(encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                yield CatalogRecord.model_validate(json.loads(line))

    def _find_record_by_note_path(self, note_path: str | None) -> CatalogRecord | None:
        normalized = (note_path or "").strip()
        normalized = normalized.removeprefix(str(self._project_root) + "/")
        normalized = normalized.lstrip("./")
        for record in self._iter_catalog_records() or []:
            if record.note_path == normalized:
                return record
        return None

    def _find_record_by_url(self, url: str) -> CatalogRecord | None:
        for record in self._iter_catalog_records() or []:
            if record.canonical_url == url or record.source_url == url:
                return record
        return None

    @staticmethod
    def _timestamped_name(timestamp, slug: str) -> str:
        return f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}-{slug}"

    @staticmethod
    def _dated_path(root: Path, timestamp, filename: str) -> Path:
        path = root / timestamp.strftime("%Y") / timestamp.strftime("%m") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _read_json_file(path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _render_note(
        workflow: WorkflowProfile,
        feed: FeedEntry,
        digest: str,
        capture_path: str,
        feed_path: str,
    ) -> str:
        comments = "\n".join(
            f"- {comment.author or 'unknown'}: {comment.text}"
            for comment in feed.comments
        )
        if not comments:
            comments = "_No comments extracted._"
        body = feed.body.strip() or "_No body extracted._"
        handoff = KnowledgeBaseStore._render_analysis_handoff(workflow.analysis)
        return "\n".join(
            [
                f"# {feed.title or feed.canonical_url}",
                "",
                f"- Source URL: {feed.source_url}",
                f"- Canonical URL: {feed.canonical_url}",
                f"- Crawler: {workflow.id}",
                f"- Collection: {workflow.kb.collection}",
                f"- Feed JSON: `{feed_path}`",
                f"- Capture JSON: `{capture_path}`",
                f"- Fetched At: {feed.fetched_at.isoformat()}",
                "",
                "## Deterministic Highlights",
                "",
                digest or "_No deterministic highlights available._",
                "",
                "## Body",
                "",
                body,
                "",
                "## Comments",
                "",
                comments,
                "",
                "## Analysis Handoff",
                "",
                handoff,
            ]
        )

    @staticmethod
    def _render_analysis_handoff(analysis: AnalysisHandoff) -> str:
        if not any([analysis.skill, analysis.instructions, analysis.deliverable]):
            return "_No skill handoff configured._"
        lines = []
        if analysis.skill:
            lines.append(f"- Recommended skill: `{analysis.skill}`")
        if analysis.deliverable:
            lines.append(f"- Deliverable: {analysis.deliverable}")
        if analysis.instructions:
            if lines:
                lines.append("")
            lines.append(analysis.instructions.strip())
        return "\n".join(lines)
