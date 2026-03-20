"""Fetching primitives for turning a URL into a raw capture."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from urllib.parse import urlparse

import httpx

from _src.models import CapturedPage, FetchMode, WorkflowFetch
from _src.router import normalize_url

logger = logging.getLogger(__name__)


class _TokenBucket:
    def __init__(self, rate: float) -> None:
        self._rate = rate
        self._tokens = rate
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            self._tokens = min(self._rate, self._tokens + (now - self._last) * self._rate)
            self._last = now
            if self._tokens < 1:
                wait = (1 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0
                return
            self._tokens -= 1


class Fetcher:
    """Fetch URLs through HTTP first, with optional browser fallback."""

    def __init__(
        self,
        user_agent: str = "Tapestry/0.1",
        timeout: int = 30,
        browser_timeout: int = 60,
        rate_limit_per_domain: float = 2.0,
    ) -> None:
        self._user_agent = user_agent
        self._timeout = timeout
        self._browser_timeout = browser_timeout
        self._buckets: dict[str, _TokenBucket] = defaultdict(lambda: _TokenBucket(rate_limit_per_domain))

    async def fetch(self, url: str, fetch_cfg: WorkflowFetch) -> CapturedPage:
        headers = dict(fetch_cfg.headers)
        strategy = fetch_cfg.mode
        fallback = fetch_cfg.fallback
        try:
            return await self._do_fetch(url, strategy, headers)
        except Exception as exc:
            logger.warning("Primary fetch failed for %s using %s: %s", url, strategy.value, exc)
            if fallback and fallback != strategy:
                return await self._do_fetch(url, fallback, headers)
            raise

    async def _do_fetch(
        self,
        url: str,
        mode: FetchMode,
        headers: dict[str, str],
    ) -> CapturedPage:
        domain = urlparse(url).hostname or ""
        await self._buckets[domain].acquire()
        if mode == FetchMode.browser:
            return await self._fetch_browser(url, headers)
        return await self._fetch_http(url, headers)

    async def _fetch_http(self, url: str, headers: dict[str, str]) -> CapturedPage:
        headers.setdefault("User-Agent", self._user_agent)
        async with httpx.AsyncClient(follow_redirects=True, timeout=self._timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            final_url = str(response.url)
            return CapturedPage(
                source_url=url,
                canonical_url=normalize_url(final_url),
                final_url=final_url,
                status_code=response.status_code,
                headers=dict(response.headers),
                fetch_mode=FetchMode.http,
                body=response.text,
            )

    async def _fetch_browser(self, url: str, headers: dict[str, str]) -> CapturedPage:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Playwright is not installed. Install with: pip install 'tapestry[browser]'") from exc

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=headers.get("User-Agent", self._user_agent))
            response = await page.goto(url, timeout=self._browser_timeout * 1000)
            await page.wait_for_load_state("networkidle")
            body = await page.content()
            final_url = page.url
            status_code = response.status if response else 0
            await browser.close()
        return CapturedPage(
            source_url=url,
            canonical_url=normalize_url(final_url),
            final_url=final_url,
            status_code=status_code,
            headers={},
            fetch_mode=FetchMode.browser,
            body=body,
        )
