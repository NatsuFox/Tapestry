#!/usr/bin/env python3
"""Publish a static frontend viewer for the Tapestry knowledge base."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the static knowledge-base viewer and JSON manifest."
    )
    parser.add_argument(
        "--project-root",
        default="",
        help="Project root containing data/books/. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--data-path",
        default="",
        help="Specific data directory to build viewer for (e.g., data/books/markets-and-trading). If not specified, builds for entire data/books/.",
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


def slugify_heading(text: str) -> str:
    slug = re.sub(r"[^\w\- ]+", "", text.strip().lower())
    slug = re.sub(r"[\s\-]+", "-", slug).strip("-")
    return slug or "section"


def extract_headings(markdown: str) -> list[dict]:
    headings: list[dict] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        if level < 1 or level > 6:
            continue
        title = stripped[level:].strip()
        if not title:
            continue
        headings.append(
            {
                "level": level,
                "title": title,
                "slug": slugify_heading(title),
            }
        )
    return headings


def extract_excerpt(markdown: str, *, limit: int = 260) -> str:
    lines = []
    for raw_line in markdown.replace("\r", "").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        if stripped.startswith("- ") or stripped.startswith("> "):
            stripped = stripped[2:].strip()
        lines.append(stripped)
        if len(" ".join(lines)) >= limit:
            break
    excerpt = " ".join(lines).strip()
    if len(excerpt) <= limit:
        return excerpt
    return excerpt[: limit - 1].rstrip() + "…"


def word_count(markdown: str) -> int:
    words = re.findall(r"\b[\w'-]+\b", markdown, flags=re.UNICODE)
    return len(words)


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
            docs[index_path.relative_to(root).as_posix()] = {
                "title": read_markdown_title(index_path),
                "path": rel_index,
                "kind": "index",
                "markdown": index_markdown,
                "excerpt": extract_excerpt(index_markdown),
                "headings": extract_headings(index_markdown),
                "wordCount": word_count(index_markdown),
                "updatedAt": int(index_path.stat().st_mtime),
                "parent": parent,
                "depth": depth,
            }

        for doc in child_docs:
            rel = doc.relative_to(root).as_posix()
            markdown = doc.read_text(encoding="utf-8")
            docs[rel] = {
                "title": read_markdown_title(doc),
                "path": rel,
                "kind": "document",
                "markdown": markdown,
                "excerpt": extract_excerpt(markdown),
                "headings": extract_headings(markdown),
                "wordCount": word_count(markdown),
                "updatedAt": int(doc.stat().st_mtime),
                "parent": relative_dir,
                "depth": depth + 1,
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
    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path.cwd().resolve()

    # Determine the data source path
    if args.data_path:
        data_source = Path(args.data_path).expanduser().resolve()
        if not data_source.is_absolute():
            data_source = project_root / args.data_path
    else:
        data_source = project_root / "data" / "books"

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

    manifest = build_tree(data_source)
    data_dir = viewer_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = data_dir / "knowledge-base.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "data_source": data_source.as_posix(),
        "viewer_root": viewer_root.as_posix(),
        "manifest_path": manifest_path.as_posix(),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
