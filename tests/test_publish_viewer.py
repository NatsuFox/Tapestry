import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "skills" / "tapestry" / "display" / "_scripts" / "publish_viewer.py"

SPEC = importlib.util.spec_from_file_location("publish_viewer", MODULE_PATH)
publish_viewer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(publish_viewer)


def test_render_markdown_document_supports_common_markdown_features():
    rendered = publish_viewer.render_markdown_document(
        """# Chapter

## Overview

- [x] done
- [ ] pending

| Name | Value |
| --- | --- |
| alpha | 1 |

See [home](../index.md#overview) and [website](https://example.com).

Reference[^1]

[^1]: Supporting detail.
""",
        current_path="guides/chapter.md",
    )

    html = rendered["html"]
    assert "<table>" in html
    assert 'type="checkbox"' in html
    assert 'href="#/index.md::overview"' in html
    assert 'data-doc-link="index.md"' in html
    assert 'data-doc-anchor="overview"' in html
    assert 'target="_blank"' in html
    assert 'rel="noreferrer noopener"' in html
    assert 'class="footnote"' in html
    assert rendered["headings"] == [
        {"level": 1, "title": "Chapter", "slug": "chapter"},
        {"level": 2, "title": "Overview", "slug": "overview"},
    ]


def test_copy_static_assets_preserves_relative_paths(tmp_path):
    data_root = tmp_path / "books"
    data_root.mkdir()
    (data_root / "index.md").write_text("# Root\n", encoding="utf-8")

    asset_dir = data_root / "guides" / "assets"
    asset_dir.mkdir(parents=True)
    asset_file = asset_dir / "diagram.png"
    asset_file.write_bytes(b"png")

    viewer_root = data_root / "_viewer"
    viewer_root.mkdir()
    stale_asset = viewer_root / "content" / "stale.txt"
    stale_asset.parent.mkdir(parents=True)
    stale_asset.write_text("old", encoding="utf-8")

    publish_viewer.copy_static_assets(data_root, viewer_root)

    copied_asset = viewer_root / "content" / "guides" / "assets" / "diagram.png"
    assert copied_asset.read_bytes() == b"png"
    assert not (viewer_root / "content" / "index.md").exists()
    assert not (viewer_root / "content" / "_viewer" / "content" / "stale.txt").exists()
