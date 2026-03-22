#!/usr/bin/env python3
"""Tapestry Subscriptions CLI.

Manage RSS/Atom source subscriptions and fetch item URLs for ingestion.

Usage:
  python run.py list
  python run.py add <name> <url> [--description TEXT]
  python run.py remove <name>
  python run.py fetch [<name> ...]
  python run.py [--json] fetch [<name> ...]
  python run.py [--project-root PATH] <subcommand>
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    print("error: httpx is required. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
# run.py lives at  <tapestry_root>/subscriptions/_scripts/run.py
# parents[0] = _scripts/   parents[1] = subscriptions/   parents[2] = tapestry root
TAPESTRY_ROOT = Path(__file__).resolve().parents[2]


def _resolve_config_path(project_root_override: str | None) -> Path:
    base = Path(project_root_override).resolve() if project_root_override else TAPESTRY_ROOT
    return base / "config" / "subscriptions.json"


# ---------------------------------------------------------------------------
# Data-store helpers
# ---------------------------------------------------------------------------

def _load(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {"sources": {}}
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _save(config_path: Path, data: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

# ---------------------------------------------------------------------------
# RSS / Atom parsing
# ---------------------------------------------------------------------------

# Atom namespace
_ATOM_NS = "http://www.w3.org/2005/Atom"


def _parse_feed(xml_bytes: bytes, source_url: str) -> list[str]:
    """Parse RSS 2.0 or Atom 1.0 and return a deduplicated list of item URLs."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"Malformed XML from {source_url}: {exc}") from exc

    urls: list[str] = []

    # --- RSS 2.0 ---
    # <rss><channel><item><link>…</link></item></channel></rss>
    if root.tag == "rss" or root.tag.endswith("}rss"):
        for item in root.iter("item"):
            link = item.findtext("link") or item.findtext("guid")
            if link and link.startswith("http"):
                urls.append(link.strip())
        return _dedupe(urls)

    # --- Atom 1.0 ---
    # <feed xmlns="http://www.w3.org/2005/Atom"><entry><link href="…"/></entry></feed>
    tag = root.tag
    if tag == f"{{{_ATOM_NS}}}feed" or tag == "feed":
        ns = _ATOM_NS if tag.startswith("{") else ""
        prefix = f"{{{ns}}}" if ns else ""
        for entry in root.iter(f"{prefix}entry"):
            for link_el in entry.findall(f"{prefix}link"):
                rel = link_el.get("rel", "alternate")
                href = link_el.get("href", "")
                if rel in ("alternate", "") and href.startswith("http"):
                    urls.append(href.strip())
                    break
        return _dedupe(urls)

    raise ValueError(f"Unrecognised feed format at {source_url} (root tag: {root.tag})")


def _dedupe(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

def cmd_list(config_path: Path, as_json: bool) -> int:
    data = _load(config_path)
    sources = data.get("sources", {})
    if as_json:
        print(json.dumps(sources, indent=2, ensure_ascii=False))
        return 0
    if not sources:
        print("No subscriptions registered. Use 'add <name> <url>' to add one.")
        return 0
    name_w = max(len(n) for n in sources) + 2
    print(f"{'NAME':<{name_w}}  {'URL':<55}  DESCRIPTION")
    print("-" * (name_w + 2 + 55 + 2 + 20))
    for name, info in sorted(sources.items()):
        url = info.get("url", "")
        desc = info.get("description", "")
        print(f"{name:<{name_w}}  {url:<55}  {desc}")
    return 0


def cmd_add(config_path: Path, name: str, url: str, description: str, as_json: bool) -> int:
    if not url.startswith("http"):
        print(f"error: URL must start with http/https (got: {url!r})", file=sys.stderr)
        return 1
    data = _load(config_path)
    sources = data.setdefault("sources", {})
    existed = name in sources
    sources[name] = {
        "url": url,
        "description": description,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(config_path, data)
    verb = "Updated" if existed else "Added"
    if as_json:
        print(json.dumps({"status": "ok", "action": verb.lower(), "name": name, "url": url}))
    else:
        print(f"{verb} source '{name}': {url}")
    return 0


def cmd_remove(config_path: Path, name: str, as_json: bool) -> int:
    data = _load(config_path)
    sources = data.get("sources", {})
    if name not in sources:
        msg = f"error: No source named '{name}'. Use 'list' to see registered sources."
        if as_json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1
    del sources[name]
    _save(config_path, data)
    if as_json:
        print(json.dumps({"status": "ok", "action": "removed", "name": name}))
    else:
        print(f"Removed source '{name}'.")
    return 0

def cmd_fetch(config_path: Path, names: list[str], as_json: bool) -> int:
    data = _load(config_path)
    sources = data.get("sources", {})
    if not sources:
        msg = "No subscriptions registered. Use 'add <name> <url>' to add one."
        if as_json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1

    # Resolve which sources to fetch
    if names:
        unknown = [n for n in names if n not in sources]
        if unknown:
            msg = f"error: Unknown source(s): {', '.join(unknown)}. Use 'list' to see registered sources."
            if as_json:
                print(json.dumps({"status": "error", "message": msg}))
            else:
                print(msg, file=sys.stderr)
            return 1
        targets = {n: sources[n] for n in names}
    else:
        targets = sources

    results: dict[str, Any] = {}
    all_urls: list[str] = []
    exit_code = 0

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        for name, info in targets.items():
            feed_url = info.get("url", "")
            try:
                resp = client.get(feed_url, headers={"User-Agent": "Tapestry/0.1 RSS Reader"})
                resp.raise_for_status()
                urls = _parse_feed(resp.content, feed_url)
                results[name] = {"status": "ok", "url": feed_url, "items": urls}
                all_urls.extend(urls)
            except Exception as exc:  # noqa: BLE001
                results[name] = {"status": "error", "url": feed_url, "error": str(exc)}
                exit_code = 1
                if not as_json:
                    print(f"[{name}] error: {exc}", file=sys.stderr)

    all_urls = _dedupe(all_urls)

    if as_json:
        print(json.dumps({"sources": results, "urls": all_urls}, indent=2, ensure_ascii=False))
    else:
        for name, res in results.items():
            if res["status"] == "ok":
                count = len(res["items"])
                print(f"[{name}] {count} item(s) from {res['url']}", file=sys.stderr)
            # errors already printed above
        for url in all_urls:
            print(url)

    return exit_code


# ---------------------------------------------------------------------------
# Argument parsing & main
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Tapestry Subscriptions: manage RSS/Atom sources and fetch item URLs.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")
    parser.add_argument("--project-root", dest="project_root", default=None,
                        help="Override tapestry project root path")

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    sub.add_parser("list", help="List all registered sources")

    p_add = sub.add_parser("add", help="Register a new RSS/Atom source")
    p_add.add_argument("name", help="Short name for the source (e.g. 'hn')")
    p_add.add_argument("url", help="RSS or Atom feed URL")
    p_add.add_argument("--description", default="", help="Human-readable description")

    p_rm = sub.add_parser("remove", help="Remove a registered source")
    p_rm.add_argument("name", help="Name of the source to remove")

    p_fetch = sub.add_parser("fetch", help="Fetch item URLs from one or all sources")
    p_fetch.add_argument("names", nargs="*", help="Source name(s) to fetch (default: all)")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    config_path = _resolve_config_path(args.project_root)

    if args.command == "list":
        return cmd_list(config_path, args.as_json)
    if args.command == "add":
        return cmd_add(config_path, args.name, args.url, args.description, args.as_json)
    if args.command == "remove":
        return cmd_remove(config_path, args.name, args.as_json)
    if args.command == "fetch":
        return cmd_fetch(config_path, args.names, args.as_json)
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())



