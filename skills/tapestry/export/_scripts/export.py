#!/usr/bin/env python3
"""Export Tapestry knowledge base content to PDF, Markdown, or HTML."""

from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_src"))
from config import TapestryConfig

# Also expose the render helper from display/_scripts
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "display" / "_scripts"))
from publish_viewer import render_markdown_document

# ── HTML template ────────────────────────────────────────────────────────────

KATEX_CSS = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"
KATEX_JS = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"
KATEX_AUTORENDER = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<link rel="stylesheet" href="{katex_css}" crossorigin="anonymous">
<style>
  body {{ max-width: 820px; margin: 40px auto; padding: 0 24px;
         font-family: Georgia, 'Times New Roman', serif; font-size: 18px;
         line-height: 1.75; color: #1a1a1a; }}
  h1,h2,h3,h4,h5,h6 {{ font-family: system-ui, sans-serif; line-height: 1.25; margin-top: 2em; }}
  h1 {{ font-size: 2em; margin-top: 0; }}
  pre {{ background: #f4f4f4; padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 0.85em; }}
  code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-size: 0.88em; }}
  pre code {{ background: none; padding: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
  th {{ background: #f0f0f0; }}
  blockquote {{ margin: 0; padding: 0 1em; border-left: 4px solid #ccc; color: #555; }}
  img {{ max-width: 100%; height: auto; }}
  a {{ color: #185d54; }}
  @media print {{ body {{ margin: 0; padding: 0 16px; font-size: 14px; }} }}
</style>
</head>
<body>
<h1>{title}</h1>
{body}
<script defer src="{katex_js}" crossorigin="anonymous"></script>
<script defer src="{katex_autorender}" crossorigin="anonymous"
  onload="renderMathInElement(document.body, {{delimiters: [{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}},{{left:'\\\\(',right:'\\\\)',display:false}},{{left:'\\\\[',right:'\\\\]',display:true}}], throwOnError: false}});"></script>
</body>
</html>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────


def safe_name(path: Path) -> str:
    stem = path.stem
    return re.sub(r"[^\w\-]+", "-", stem).strip("-").lower() or "export"


def embed_images(html: str, source_md_path: Path) -> str:
    """Replace local <img src="..."> with base64 data URIs for portability."""
    def replace_src(m: re.Match) -> str:
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        img_path = (source_md_path.parent / src).resolve()
        if not img_path.exists():
            return m.group(0)
        suffix = img_path.suffix.lower().lstrip(".")
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}.get(suffix, "image/png")
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        return f'src="data:{mime};base64,{b64}"'
    return re.sub(r'src="([^"]+)"', replace_src, html)


def render_html(md_text: str, md_path: Path, title: str) -> str:
    rendered = render_markdown_document(md_text, current_path=md_path.name)
    body = embed_images(rendered["html"], md_path)
    return HTML_TEMPLATE.format(
        title=title,
        body=body,
        katex_css=KATEX_CSS,
        katex_js=KATEX_JS,
        katex_autorender=KATEX_AUTORENDER,
    )

def read_title(md_path: Path) -> str:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return md_path.stem.replace("-", " ").replace("_", " ").title()


# ── Scope collectors ─────────────────────────────────────────────────────────


def collect_file(target: Path) -> list[Path]:
    if not target.exists():
        raise FileNotFoundError(f"Target not found: {target}")
    return [target]


def collect_note(target: Path) -> list[Path]:
    if not target.exists():
        raise FileNotFoundError(f"Note not found: {target}")
    return [target]


def collect_feed(target: Path) -> list[Path]:
    """Returns the feed JSON path; we export the body field as Markdown."""
    if not target.exists():
        raise FileNotFoundError(f"Feed not found: {target}")
    return [target]


def collect_kb(books_root: Path) -> list[Path]:
    return sorted(books_root.rglob("*.md"))


# ── Exporters ─────────────────────────────────────────────────────────────────


def export_markdown(sources: list[Path], out_root: Path, scope: str, books_root: Path) -> list[Path]:
    out_dir = out_root / "markdown"
    exported = []
    for src in sources:
        if scope == "feed":
            data = json.loads(src.read_text(encoding="utf-8"))
            text = data.get("body", "")
            dest = out_dir / src.with_suffix(".md").name
        else:
            text = src.read_text(encoding="utf-8")
            try:
                rel = src.relative_to(books_root)
                dest = out_dir / rel
            except ValueError:
                dest = out_dir / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        exported.append(dest)
    return exported


def export_html(sources: list[Path], out_root: Path, scope: str, books_root: Path) -> list[Path]:
    out_dir = out_root / "html"
    exported = []
    for src in sources:
        if scope == "feed":
            data = json.loads(src.read_text(encoding="utf-8"))
            md_text = data.get("body", "")
            title = data.get("title", src.stem)
            dest = out_dir / src.with_suffix(".html").name
            # No local images in feed JSON, so embed_images is a no-op
            rendered = render_markdown_document(md_text, current_path=src.name)
            html = HTML_TEMPLATE.format(
                title=title, body=rendered["html"],
                katex_css=KATEX_CSS, katex_js=KATEX_JS, katex_autorender=KATEX_AUTORENDER,
            )
        else:
            md_text = src.read_text(encoding="utf-8")
            title = read_title(src)
            try:
                rel = src.relative_to(books_root)
                dest = out_dir / rel.with_suffix(".html")
            except ValueError:
                dest = out_dir / src.with_suffix(".html").name
            html = render_html(md_text, src, title)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        exported.append(dest)
    return exported


def export_pdf(sources: list[Path], out_root: Path, scope: str, books_root: Path) -> list[Path]:
    """Export to PDF using Playwright. Falls back to self-printing HTML if unavailable."""
    out_dir = out_root / "pdf"
    exported = []
    playwright_available = False
    try:
        from playwright.sync_api import sync_playwright
        playwright_available = True
    except ImportError:
        print("[export] Playwright not installed. Falling back to self-printing HTML.", file=sys.stderr)
        print("[export] Install with: pip install playwright && playwright install chromium", file=sys.stderr)

    for src in sources:
        if scope == "feed":
            data = json.loads(src.read_text(encoding="utf-8"))
            md_text = data.get("body", "")
            title = data.get("title", src.stem)
            rendered = render_markdown_document(md_text, current_path=src.name)
            html = HTML_TEMPLATE.format(
                title=title, body=rendered["html"],
                katex_css=KATEX_CSS, katex_js=KATEX_JS, katex_autorender=KATEX_AUTORENDER,
            )
            base_name = src.stem
        else:
            md_text = src.read_text(encoding="utf-8")
            title = read_title(src)
            html = render_html(md_text, src, title)
            base_name = src.stem

        try:
            rel = src.relative_to(books_root)
            dest_base = out_dir / rel.parent / base_name
        except ValueError:
            dest_base = out_dir / base_name

        if playwright_available:
            dest = dest_base.with_suffix(".pdf")
            dest.parent.mkdir(parents=True, exist_ok=True)
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html, wait_until="networkidle")
                page.pdf(path=str(dest), format="A4", print_background=True)
                browser.close()
        else:
            # Fallback: self-printing HTML
            dest = dest_base.with_suffix(".print.html")
            dest.parent.mkdir(parents=True, exist_ok=True)
            print_html = html.replace(
                "</body>",
                "<script>window.addEventListener('load', function() { window.print(); });</script>\n</body>"
            )
            dest.write_text(print_html, encoding="utf-8")
        exported.append(dest)
    return exported


# ── CLI ───────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export Tapestry KB content to PDF/Markdown/HTML.")
    parser.add_argument("--format", default="all", choices=["pdf", "markdown", "html", "all"])
    parser.add_argument("--scope", default="kb", choices=["file", "note", "feed", "kb"])
    parser.add_argument("--target", default="", help="Path to specific source file (for file/note/feed scopes)")
    parser.add_argument("--project-root", default="", help="Override project root")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    config = TapestryConfig.load()
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else config.resolve_project_root()
    data_root = config.resolve_data_root(project_root)
    books_root = data_root / "books"
    out_root = data_root / "exports"

    # Resolve sources
    scope = args.scope
    if scope == "kb":
        sources = collect_kb(books_root)
    elif scope in ("file", "note"):
        if not args.target:
            print(f"[export] --target is required for scope '{scope}'", file=sys.stderr)
            return 1
        target = Path(args.target).expanduser()
        if not target.is_absolute():
            target = (project_root / target).resolve()
        sources = collect_file(target)
    elif scope == "feed":
        if not args.target:
            print("[export] --target is required for scope 'feed'", file=sys.stderr)
            return 1
        target = Path(args.target).expanduser()
        if not target.is_absolute():
            target = (project_root / target).resolve()
        sources = collect_feed(target)
    else:
        print(f"[export] Unknown scope: {scope}", file=sys.stderr)
        return 1

    if not sources:
        print("[export] No source files found.", file=sys.stderr)
        return 1

    result: dict[str, list[str]] = {}
    formats = ["markdown", "html", "pdf"] if args.format == "all" else [args.format]

    for fmt in formats:
        if fmt == "markdown":
            paths = export_markdown(sources, out_root, scope, books_root)
        elif fmt == "html":
            paths = export_html(sources, out_root, scope, books_root)
        elif fmt == "pdf":
            paths = export_pdf(sources, out_root, scope, books_root)
        else:
            continue
        result[fmt] = [str(p) for p in paths]
        print(f"[export] {fmt}: {len(paths)} file(s) → {out_root / fmt}", file=sys.stderr)

    print(json.dumps({"output_root": str(out_root), "exports": result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
