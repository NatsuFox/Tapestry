from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

UI_ROOT = Path(__file__).resolve().parents[1] / "src" / "ui"
SITE_ROOT = "https://natsufox.github.io/Tapestry/"
PAGES = {
    "index.html": SITE_ROOT,
    "install.html": f"{SITE_ROOT}install.html",
    "supported-sources.html": f"{SITE_ROOT}supported-sources.html",
    "use-cases.html": f"{SITE_ROOT}use-cases.html",
    "faq.html": f"{SITE_ROOT}faq.html",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_text(path: Path) -> str:
    require(path.exists(), f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def check_page(filename: str, canonical_url: str) -> None:
    text = read_text(UI_ROOT / filename)
    require(f'<link rel="canonical" href="{canonical_url}" />' in text, f"missing canonical in {filename}")
    require('name="description"' in text, f"missing description in {filename}")
    require('name="robots"' in text, f"missing robots meta in {filename}")
    require('property="og:title"' in text, f"missing og:title in {filename}")
    require('summary_large_image' in text, f"missing twitter card in {filename}")
    require('<script type="application/ld+json">' in text, f"missing structured data in {filename}")
    require('<h1' in text, f"missing h1 in {filename}")


def main() -> int:
    for filename, canonical_url in PAGES.items():
        check_page(filename, canonical_url)

    index_html = read_text(UI_ROOT / "index.html")
    for href in ["./install.html", "./supported-sources.html", "./use-cases.html", "./faq.html"]:
        require(href in index_html, f"homepage is missing internal link {href}")

    robots_text = read_text(UI_ROOT / "robots.txt")
    require("Allow: /" in robots_text, "robots.txt must allow crawling")
    require(
        "Sitemap: https://natsufox.github.io/Tapestry/sitemap.xml" in robots_text,
        "robots.txt must advertise sitemap.xml",
    )

    google_verification = read_text(UI_ROOT / "googlecd228347c7ec0eec.html")
    require("google-site-verification" in google_verification, "google verification file is missing content")

    sitemap_tree = ET.fromstring(read_text(UI_ROOT / "sitemap.xml"))
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {loc.text for loc in sitemap_tree.findall("sm:url/sm:loc", ns)}
    require(locs == set(PAGES.values()), f"sitemap locs do not match expected pages: {sorted(locs)}")

    print("Portal SEO checks passed for", len(PAGES), "pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
