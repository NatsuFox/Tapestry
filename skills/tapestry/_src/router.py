"""URL normalization and workflow matching."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent matching and storage."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() or "https"
    host = (parsed.hostname or "").lower().removeprefix("www.")
    port = (
        f":{parsed.port}"
        if parsed.port and parsed.port not in (80, 443)
        else ""
    )
    path = parsed.path.rstrip("/") or ""
    query = urlencode(sorted(parse_qs(parsed.query, keep_blank_values=True).items()), doseq=True)
    return urlunparse((scheme, f"{host}{port}", path, "", query, ""))


def extract_domain(url: str) -> str:
    """Return the bare host without a leading www."""
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


class ProfileRouter:
    """Resolve URLs to profile identifiers using domain and regex matching."""

    def __init__(self) -> None:
        self._domain_index: dict[str, list[tuple[str, list[re.Pattern[str]]]]] = {}
        self._global_patterns: list[tuple[str, list[re.Pattern[str]]]] = []

    def register(self, workflow_id: str, domains: list[str], url_patterns: list[str]) -> None:
        compiled = [re.compile(pattern) for pattern in url_patterns]
        if domains:
            for domain in domains:
                normalized = domain.lower().removeprefix("www.")
                self._domain_index.setdefault(normalized, []).append((workflow_id, compiled))
            return
        if compiled:
            self._global_patterns.append((workflow_id, compiled))

    def unregister(self, workflow_id: str) -> None:
        for domain, entries in list(self._domain_index.items()):
            self._domain_index[domain] = [
                (entry_id, patterns)
                for entry_id, patterns in entries
                if entry_id != workflow_id
            ]
            if not self._domain_index[domain]:
                del self._domain_index[domain]
        self._global_patterns = [
            (entry_id, patterns)
            for entry_id, patterns in self._global_patterns
            if entry_id != workflow_id
        ]

    def match(self, url: str) -> str | None:
        domain = extract_domain(url)
        if domain in self._domain_index:
            for workflow_id, patterns in self._domain_index[domain]:
                if not patterns:
                    return workflow_id
                for pattern in patterns:
                    if pattern.search(url):
                        return workflow_id
        for workflow_id, patterns in self._global_patterns:
            for pattern in patterns:
                if pattern.search(url):
                    return workflow_id
        return None


WorkflowRouter = ProfileRouter


CrawlerRouter = ProfileRouter
