"""Pydantic models for crawlers, feed entries, and ingest results."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class FetchMode(str, Enum):
    http = "http"
    browser = "browser"


class WorkflowMeta(BaseModel):
    title: str
    description: str = ""
    content_type: str = "article"


class WorkflowMatch(BaseModel):
    domains: list[str] = Field(default_factory=list)
    url_patterns: list[str] = Field(default_factory=list)


class WorkflowFetch(BaseModel):
    mode: FetchMode = FetchMode.http
    headers: dict[str, str] = Field(default_factory=dict)
    fallback: FetchMode | None = FetchMode.browser


class CommentRule(BaseModel):
    container: str = ""
    author: str = ""
    text: str = ""
    max_count: int = 30


class WorkflowParse(BaseModel):
    title: str = ""
    author: str = ""
    published_at: str = ""
    body: str = ""
    comments: CommentRule | None = None


class AnalysisHandoff(BaseModel):
    skill: str = ""
    instructions: str = ""
    deliverable: str = ""

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_prompt(cls, data: Any) -> Any:
        if isinstance(data, dict) and "instructions" not in data and "prompt" in data:
            migrated = dict(data)
            migrated["instructions"] = migrated.pop("prompt", "")
            return migrated
        return data


class WorkflowKnowledgeBase(BaseModel):
    collection: str = "inbox"


class WorkflowProfile(BaseModel):
    id: str
    meta: WorkflowMeta
    match: WorkflowMatch = Field(default_factory=WorkflowMatch)
    fetch: WorkflowFetch = Field(default_factory=WorkflowFetch)
    parse: WorkflowParse = Field(default_factory=WorkflowParse)
    analysis: AnalysisHandoff = Field(default_factory=AnalysisHandoff)
    kb: WorkflowKnowledgeBase = Field(default_factory=WorkflowKnowledgeBase)

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_summarize(cls, data: Any) -> Any:
        if isinstance(data, dict) and "analysis" not in data and "summarize" in data:
            migrated = dict(data)
            migrated["analysis"] = migrated.pop("summarize")
            return migrated
        return data


class FeedComment(BaseModel):
    author: str | None = None
    text: str


class CapturedPage(BaseModel):
    id: str = Field(default_factory=_uuid)
    source_url: str
    canonical_url: str
    final_url: str
    status_code: int
    headers: dict[str, str] = Field(default_factory=dict)
    fetch_mode: FetchMode = FetchMode.http
    fetched_at: datetime = Field(default_factory=_now)
    body: str = ""


class FeedEntry(BaseModel):
    id: str = Field(default_factory=_uuid)
    source_url: str
    canonical_url: str
    workflow_id: str
    content_type: str = "article"
    title: str = ""
    author: str | None = None
    published_at: datetime | None = None
    body: str = ""
    comments: list[FeedComment] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    content_hash: str = ""
    fetched_at: datetime = Field(default_factory=_now)
    capture_path: str = ""

    def compute_content_hash(self) -> str:
        comment_blob = "\n".join(comment.text for comment in self.comments)
        payload = "\n".join(
            [
                self.title.strip(),
                self.body.strip(),
                comment_blob.strip(),
            ]
        )
        self.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self.content_hash


class CatalogRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=_uuid)
    source_url: str
    canonical_url: str
    workflow_id: str
    collection: str
    title: str = ""
    digest: str = Field(default="", validation_alias=AliasChoices("digest", "summary"))
    analysis: AnalysisHandoff = Field(default_factory=AnalysisHandoff)
    content_hash: str = ""
    capture_path: str
    feed_path: str
    note_path: str
    stored_at: datetime = Field(default_factory=_now)


class IngestResult(BaseModel):
    source_url: str
    canonical_url: str
    workflow_id: str
    collection: str
    title: str = ""
    status: str
    digest: str = Field(default="", validation_alias=AliasChoices("digest", "summary"))
    analysis: AnalysisHandoff = Field(default_factory=AnalysisHandoff)
    capture_path: str
    feed_path: str
    note_path: str


class BatchIngestReport(BaseModel):
    requested_urls: list[str]
    results: list[IngestResult] = Field(default_factory=list)
    stored_count: int = 0
    duplicate_count: int = 0


WorkflowSummarize = AnalysisHandoff
