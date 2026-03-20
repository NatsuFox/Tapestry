"""Unified crawler entrypoint for all code-defined crawler modules."""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

from _src.config import TapestryConfig
from _src.ingest import IngestionService
from _src.registry import CrawlerRegistry

URL_RE = re.compile(r"https?://[^\s<>()\[\]{}\"']+")


def extract_urls(*chunks: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for chunk in chunks:
        if not chunk:
            continue
        for match in URL_RE.findall(chunk):
            url = match.rstrip(".,);]}>")
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Tapestry crawlers through the unified code-defined registry.")
    parser.add_argument("inputs", nargs="*", help="URLs or free-form text containing URLs")
    parser.add_argument("--text", default="", help="Optional free-form context to scan for URLs")
    parser.add_argument("--json", action="store_true", help="Emit the batch report as JSON")
    parser.add_argument(
        "--project-root",
        default="",
        help="Optional project root where data and knowledge-base artifacts should be written",
    )
    parser.add_argument(
        "--crawler",
        default="auto",
        help="Force a specific crawler id instead of automatic matching",
    )
    parser.add_argument(
        "--list-crawlers",
        action="store_true",
        help="List available crawler ids and exit",
    )
    return parser


def _render_list(registry: CrawlerRegistry) -> str:
    lines = []
    for crawler in registry.list():
        lines.append(f"{crawler.id}\t{crawler.title}")
    return "\n".join(lines)


async def run_cli(args: argparse.Namespace) -> int:
    registry = CrawlerRegistry()
    if args.list_crawlers:
        print(_render_list(registry))
        return 0

    input_blob = " ".join(args.inputs).strip()
    combined_text = "\n".join(part for part in [args.text, input_blob] if part).strip()
    urls = extract_urls(input_blob, combined_text)
    if not urls:
        raise ValueError("No URLs found. Pass URLs directly or use --text.")

    # Load config and validate/fix project root
    from _src.config import find_project_root, validate_and_fix_project_root

    target_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd().resolve()

    # Try to find and load config
    config_candidates = [
        Path(__file__).resolve().parents[2] / "config" / "tapestry.config.json",  # skills/tapestry/config/
        target_root / "tapestry.config.json",  # Project root (legacy)
        target_root / "skills" / "tapestry" / "config" / "tapestry.config.json",  # From project root
    ]

    config_path = None
    for candidate in config_candidates:
        if candidate.exists():
            config_path = candidate
            break

    # Validate and auto-correct project root if needed
    if config_path:
        target_root = validate_and_fix_project_root(config_path, target_root)
    else:
        # No config found, try to find project root automatically
        found_root = find_project_root(target_root)
        if found_root:
            target_root = found_root

    config = TapestryConfig.load()  # Will find config in skills/tapestry/config/
    service = IngestionService.for_project_root(target_root, registry=registry)
    report = await service.ingest_urls(urls, forced_crawler_id=None if args.crawler == "auto" else args.crawler)

    if args.json:
        print(report.model_dump_json(indent=2))
        return 0

    print(
        f"Processed {len(report.requested_urls)} URL(s): "
        f"{report.stored_count} stored, {report.duplicate_count} duplicates."
    )

    synthesis_urls = []
    for result in report.results:
        # Convert relative paths to absolute paths for display
        feed_abs = (target_root / result.feed_path).resolve()
        note_abs = (target_root / result.note_path).resolve()

        print(
            f"[{result.status}] {result.title or result.canonical_url}\n"
            f"  crawler={result.workflow_id} collection={result.collection}\n"
            f"  feed={feed_abs}\n"
            f"  note={note_abs}\n"
            f"  analysis_skill={result.analysis.skill or '-'}"
        )

        # Collect URLs for synthesis if status is 'stored' and synthesis is configured
        if result.status == "stored" and result.analysis.skill:
            synthesis_urls.append(result.canonical_url)

    # Auto-synthesis if configured
    if config.should_auto_synthesize() and synthesis_urls:
        print(f"\n[Auto-synthesis enabled] Triggering synthesis for {len(synthesis_urls)} URL(s)...")
        print("Note: Synthesis requires the tapestry-synthesis skill to be invoked by the agent.")
        print(f"URLs to synthesize: {', '.join(synthesis_urls)}")

    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(run_cli(args))
    except ValueError as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
