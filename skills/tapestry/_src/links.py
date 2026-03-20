"""Helpers for extracting URLs from free-form user text."""

from __future__ import annotations

import re

_URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")
_TRAILING_PUNCTUATION = ".,;:!?)>]}'\""


def extract_urls(text: str) -> list[str]:
    """Extract and de-duplicate URLs while preserving order."""
    seen: set[str] = set()
    urls: list[str] = []
    for raw_url in _URL_PATTERN.findall(text):
        candidate = raw_url.rstrip(_TRAILING_PUNCTUATION)
        if candidate and candidate not in seen:
            seen.add(candidate)
            urls.append(candidate)
    return urls
