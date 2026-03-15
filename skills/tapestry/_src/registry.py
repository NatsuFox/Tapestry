"""Code-defined crawler registry for the Tapestry skill pack."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable

from _src.fetch import Fetcher
from _src.models import CapturedPage, FeedEntry, WorkflowProfile
from _src.parse import Parser


@dataclass(slots=True)
class CrawlerProduct:
    workflow: WorkflowProfile
    capture: CapturedPage
    feed: FeedEntry


CrawlHandler = Callable[
    [str, Path, "CrawlerDefinition", Fetcher, Parser],
    Awaitable[CrawlerProduct],
]


@dataclass(slots=True)
class CrawlerDefinition:
    id: str
    title: str
    domains: list[str] = field(default_factory=list)
    url_patterns: list[str] = field(default_factory=list)
    workflow: WorkflowProfile | None = None
    handler: CrawlHandler | None = None

    def matches(self, url: str, *, domain: str) -> bool:
        normalized_domains = [item.lower().removeprefix("www.") for item in self.domains]
        if normalized_domains and domain not in normalized_domains:
            return False
        if self.url_patterns and not any(re.search(pattern, url) for pattern in self.url_patterns):
            return False
        return bool(normalized_domains or self.url_patterns)


class CrawlerRegistry:
    """Match URLs to code-defined crawler implementations."""

    def __init__(self, crawlers: list[CrawlerDefinition] | None = None) -> None:
        self._crawlers = crawlers or self._default_crawlers()

    def list(self) -> list[CrawlerDefinition]:
        return list(self._crawlers)

    def get(self, crawler_id: str) -> CrawlerDefinition | None:
        for crawler in self._crawlers:
            if crawler.id == crawler_id:
                return crawler
        return None

    def match(self, url: str) -> CrawlerDefinition:
        from _src.router import extract_domain

        domain = extract_domain(url)
        fallback: CrawlerDefinition | None = None
        for crawler in self._crawlers:
            if crawler.matches(url, domain=domain):
                return crawler
            if not crawler.domains and not crawler.url_patterns:
                fallback = crawler
        if fallback is not None:
            return fallback
        raise LookupError(f"No crawler matched the URL: {url}")

    @staticmethod
    def _default_crawlers() -> list[CrawlerDefinition]:
        from _src.crawlers.generic_html import CRAWLER as GENERIC_HTML
        from _src.crawlers.hackernews import CRAWLER as HACKERNEWS
        from _src.crawlers.reddit import CRAWLER as REDDIT
        from _src.crawlers.weibo import CRAWLER as WEIBO
        from _src.crawlers.x import CRAWLER as X
        from _src.crawlers.xiaohongshu import CRAWLER as XIAOHONGSHU
        from _src.crawlers.zhihu import CRAWLER as ZHIHU

        return [ZHIHU, X, XIAOHONGSHU, WEIBO, HACKERNEWS, REDDIT, GENERIC_HTML]
