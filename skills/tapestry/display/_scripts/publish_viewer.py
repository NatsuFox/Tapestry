#!/usr/bin/env python3
"""Publish a static frontend viewer for the Tapestry knowledge base."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_src"))
from config import TapestryConfig

STATIC_CONTENT_DIR = "content"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the static knowledge-base viewer and JSON manifest."
    )
    parser.add_argument(
        "--project-root",
        default="",
        help="Project root containing the Tapestry skill-local _data/ tree. Defaults to the installed skill root.",
    )
    parser.add_argument(
        "--data-path",
        default="",
        help="Specific data directory to build viewer for (e.g., _data/books/markets-and-trading). If not specified, builds for the entire _data/books/ tree.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the existing frontend bundle if present.",
    )
    return parser


def read_markdown_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def slugify_heading(text: str, separator: str = "-") -> str:
    slug = re.sub(r"[^\w\- ]+", "", text.strip().lower())
    slug = re.sub(r"[\s\-]+", separator, slug).strip(separator)
    return slug or "section"


def normalize_relative_path(current_path: str, raw_path: str) -> str:
    if raw_path.startswith("/"):
        raw_parts = raw_path.split("/")
    else:
        current_parts = current_path.split("/")[:-1]
        raw_parts = [*current_parts, *raw_path.split("/")]

    normalized: list[str] = []
    for part in raw_parts:
        if not part or part == ".":
            continue
        if part == "..":
            if normalized:
                normalized.pop()
            continue
        normalized.append(part)
    return "/".join(normalized)


def resolve_viewer_link(current_path: str, raw_target: str) -> dict[str, str]:
    parsed = urlsplit(raw_target.strip())
    if parsed.scheme or parsed.netloc:
        return {"kind": "external", "href": raw_target}

    if not parsed.path and parsed.fragment:
        return {
            "kind": "document",
            "path": current_path,
            "anchor": parsed.fragment,
        }

    normalized_path = normalize_relative_path(current_path, parsed.path)
    if normalized_path.endswith(".md"):
        return {
            "kind": "document",
            "path": normalized_path,
            "anchor": parsed.fragment,
        }

    href = f"{STATIC_CONTENT_DIR}/{normalized_path}" if normalized_path else ""
    if parsed.query:
        href = f"{href}?{parsed.query}"
    if parsed.fragment:
        href = f"{href}#{parsed.fragment}"
    return {"kind": "asset", "href": href}


class ViewerLinkTreeprocessor(Treeprocessor):
    def __init__(self, md: markdown.Markdown, *, current_path: str) -> None:
        super().__init__(md)
        self.current_path = current_path

    def run(self, root):  # type: ignore[override]
        for element in root.iter():
            if element.tag == "a":
                self._rewrite_anchor(element)
            elif element.tag == "img":
                self._rewrite_image(element)
        return root

    def _rewrite_anchor(self, element) -> None:
        href = element.get("href")
        if not href:
            return

        resolved = resolve_viewer_link(self.current_path, href)
        if resolved["kind"] == "document":
            viewer_href = f"#/{resolved['path']}"
            if resolved.get("anchor"):
                viewer_href = f"{viewer_href}::{resolved['anchor']}"
                element.set("data-doc-anchor", resolved["anchor"])
            element.set("href", viewer_href)
            element.set("data-doc-link", resolved["path"])
            return

        if resolved["kind"] == "asset":
            element.set("href", resolved["href"])
            return

        element.set("target", "_blank")
        element.set("rel", "noreferrer noopener")

    def _rewrite_image(self, element) -> None:
        src = element.get("src")
        if not src:
            return
        resolved = resolve_viewer_link(self.current_path, src)
        if resolved["kind"] == "asset":
            element.set("src", resolved["href"])
        element.set("loading", "lazy")
        element.set("decoding", "async")


class ViewerLinkExtension(Extension):
    def __init__(self, *, current_path: str) -> None:
        super().__init__()
        self.current_path = current_path

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(
            ViewerLinkTreeprocessor(md, current_path=self.current_path),
            "viewer_link_rewriter",
            5,
        )


def flatten_toc_tokens(tokens: list[dict]) -> list[dict]:
    headings: list[dict] = []
    for token in tokens:
        headings.append(
            {
                "level": int(token.get("level", 1)),
                "title": token.get("name", ""),
                "slug": token.get("id", "section"),
            }
        )
        headings.extend(flatten_toc_tokens(token.get("children", [])))
    return headings


def render_markdown_document(markdown_text: str, *, current_path: str) -> dict:
    renderer = markdown.Markdown(
        extensions=[
            "extra",
            "admonition",
            "sane_lists",
            "toc",
            "pymdownx.tasklist",
            "pymdownx.superfences",
            "pymdownx.arithmatex",
            ViewerLinkExtension(current_path=current_path),
        ],
        extension_configs={
            "toc": {
                "slugify": slugify_heading,
                "permalink": False,
            },
            "pymdownx.tasklist": {
                "custom_checkbox": False,
                "clickable_checkbox": False,
            },
            "pymdownx.arithmatex": {
                "generic": True,
            },
        },
        output_format="html5",
    )
    html = renderer.convert(markdown_text)
    headings = flatten_toc_tokens(getattr(renderer, "toc_tokens", []))
    return {
        "html": html,
        "headings": headings,
    }


def extract_excerpt(markdown: str, *, limit: int = 400) -> str:
    lines = []
    char_count = 0
    in_code_block = False
    in_math_block = False

    for raw_line in markdown.replace("\r", "").splitlines():
        stripped = raw_line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Track display math blocks ($$)
        if stripped.startswith("$$"):
            in_math_block = not in_math_block
            continue

        # Skip content inside code or math blocks
        if in_code_block or in_math_block:
            continue

        # Skip empty lines, headers, and metadata
        if not stripped or stripped.startswith("#"):
            continue

        # Skip metadata lines (lines starting with "- " followed by a label)
        if stripped.startswith("- ") and ":" in stripped[:50]:
            continue

        # Skip bold-key metadata lines: **Key**: value (common in synthesis docs)
        if re.match(r'^\*\*[^*]+\*\*\s*:', stripped):
            continue

        # Skip blockquote metadata lines: > **Key**: value
        if re.match(r'^>\s*\*\*[^*]+\*\*\s*:', stripped):
            continue

        # Skip plain key: value metadata lines at top of doc (e.g. "Source: url")
        if re.match(r'^[A-Z][\w ]{1,30}:\s+\S', stripped):
            continue

        # Skip lines with display math delimiters
        if stripped.startswith("\\[") or stripped.startswith("\\]"):
            continue

        # Handle blockquotes
        if stripped.startswith("> "):
            stripped = stripped[2:].strip()

        lines.append(stripped)
        char_count += len(stripped) + 1  # +1 for newline
        if char_count >= limit:
            break

    # Join with newlines to preserve paragraph structure
    excerpt = "\n".join(lines).strip()
    if len(excerpt) <= limit:
        return excerpt
    return excerpt[: limit - 1].rstrip() + "…"


def word_count(markdown: str) -> int:
    words = re.findall(r"\b[\w'-]+\b", markdown, flags=re.UNICODE)
    return len(words)


def copy_static_assets(root: Path, viewer_root: Path) -> None:
    content_root = viewer_root / STATIC_CONTENT_DIR
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() == ".md":
            continue
        if path.is_relative_to(viewer_root):
            continue
        destination = content_root / path.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def build_tree(root: Path) -> dict:
    docs = {}

    def walk(directory: Path, *, depth: int = 0, parent: str | None = None) -> dict:
        relative_dir = "." if directory == root else directory.relative_to(root).as_posix()
        index_path = directory / "index.md"
        child_dirs = sorted(
            [item for item in directory.iterdir() if item.is_dir() and item.name != "_viewer"],
            key=lambda item: item.name,
        )
        child_docs = sorted(
            [item for item in directory.glob("*.md") if item.name != "index.md"],
            key=lambda item: item.name,
        )

        index_markdown = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        index_rendered = (
            render_markdown_document(index_markdown, current_path=index_path.relative_to(root).as_posix())
            if index_path.exists()
            else None
        )
        node = {
            "path": relative_dir,
            "title": read_markdown_title(index_path) if index_path.exists() else directory.name.replace("-", " ").title(),
            "index": index_path.relative_to(root).as_posix() if index_path.exists() else None,
            "excerpt": extract_excerpt(index_markdown) if index_markdown else "",
            "children": [],
            "documents": [],
            "depth": depth,
            "parent": parent,
        }

        if index_path.exists():
            rel_index = index_path.relative_to(root).as_posix()
            index_glossary_path = index_path.with_suffix(".glossary.json")
            index_glossary = json.loads(index_glossary_path.read_text(encoding="utf-8")) if index_glossary_path.exists() else {}
            docs[index_path.relative_to(root).as_posix()] = {
                "title": read_markdown_title(index_path),
                "path": rel_index,
                "kind": "index",
                "markdown": index_markdown,
                "html": index_rendered["html"],
                "excerpt": extract_excerpt(index_markdown),
                "headings": index_rendered["headings"],
                "wordCount": word_count(index_markdown),
                "updatedAt": int(index_path.stat().st_mtime),
                "parent": parent,
                "depth": depth,
                "tags": index_glossary.get("tags", []),
                "categories": index_glossary.get("categories", []),
                "glossary": index_glossary.get("terms", []),
            }

        for doc in child_docs:
            rel = doc.relative_to(root).as_posix()
            markdown = doc.read_text(encoding="utf-8")
            rendered = render_markdown_document(markdown, current_path=rel)
            glossary_path = doc.with_suffix(".glossary.json")
            glossary = json.loads(glossary_path.read_text(encoding="utf-8")) if glossary_path.exists() else {}
            docs[rel] = {
                "title": read_markdown_title(doc),
                "path": rel,
                "kind": "document",
                "markdown": markdown,
                "html": rendered["html"],
                "excerpt": extract_excerpt(markdown),
                "headings": rendered["headings"],
                "wordCount": word_count(markdown),
                "updatedAt": int(doc.stat().st_mtime),
                "parent": relative_dir,
                "depth": depth + 1,
                "tags": glossary.get("tags", []),
                "categories": glossary.get("categories", []),
                "glossary": glossary.get("terms", []),
            }
            node["documents"].append(rel)

        for child in child_dirs:
            node["children"].append(walk(child, depth=depth + 1, parent=relative_dir))

        node["documentCount"] = len(node["documents"]) + sum(child["documentCount"] for child in node["children"])
        node["sectionCount"] = len(node["children"])

        return node

    root_node = walk(root)
    return {
        "generatedAt": int(root.stat().st_mtime) if root.exists() else None,
        "root": root_node,
        "documents": docs,
        "documentCount": len(docs),
    }


def main() -> int:
    args = build_parser().parse_args()

    # Load Tapestry configuration
    config = TapestryConfig.load()
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else config.resolve_project_root()
    data_root = config.resolve_data_root(project_root)

    # Determine the data source path
    if args.data_path:
        requested = Path(args.data_path).expanduser()
        if requested.is_absolute():
            data_source = requested
        else:
            project_candidate = project_root / args.data_path
            data_source = project_candidate if project_candidate.exists() else data_root / args.data_path
    else:
        data_source = data_root / "books"

    data_source = data_source.resolve()

    if not data_source.exists():
        raise SystemExit(f"Data source {data_source} does not exist.")

    # Determine viewer output path
    viewer_root = data_source / "_viewer"
    if viewer_root.exists() and args.force:
        shutil.rmtree(viewer_root)
    viewer_root.mkdir(parents=True, exist_ok=True)

    ui_root = Path(__file__).resolve().parent.parent / "_ui"

    # Copy UI files, but skip the data symlink if it exists
    for item in ui_root.iterdir():
        if item.name == "data" and item.is_symlink():
            continue
        dest = viewer_root / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # Inject font configuration into CSS
    css_path = viewer_root / "assets" / "styles.css"
    if css_path.exists():
        css_content = css_path.read_text(encoding="utf-8")
        # Update the --font-ui variable with configured fonts
        css_content = re.sub(
            r'--font-ui:\s*"[^"]+",\s*"[^"]+",\s*sans-serif;',
            f'--font-ui: "{config.fonts.en_font}", "{config.fonts.zh_font}", sans-serif;',
            css_content
        )
        css_path.write_text(css_content, encoding="utf-8")

    manifest = build_tree(data_source)
    copy_static_assets(data_source, viewer_root)
    data_dir = viewer_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = data_dir / "knowledge-base.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "data_source": data_source.as_posix(),
        "viewer_root": viewer_root.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "fonts": {
            "en_font": config.fonts.en_font,
            "zh_font": config.fonts.zh_font,
        }
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
