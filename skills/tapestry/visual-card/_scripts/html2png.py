#!/usr/bin/env python3
"""
html2png.py — 将视觉笔记卡片 HTML 渲染为高清 PNG 图片
依赖: pip install playwright && playwright install chromium

用法:
    python html2png.py <input.html> [output.png] [--scale=1.5]

示例:
    python html2png.py card.html                     # 输出 card.png (1.5x)
    python html2png.py card.html poster.png           # 指定输出文件名
    python html2png.py card.html --scale=2            # 2x 超清
    python html2png.py card.html poster.png --scale=1 # 1x 标准
"""

import sys
import argparse
from pathlib import Path


def html_to_png(input_html: str, output_png: str = None, scale: float = 1.5):
    """
    用 Playwright 无头 Chromium 将 HTML 渲染为 PNG。
    只截取 .poster 元素，不包含悬浮按钮等页面外元素。
    """
    from playwright.sync_api import sync_playwright

    input_path = Path(input_html).resolve()
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return None

    if output_png is None:
        output_png = str(input_path.with_suffix(".png"))
    output_path = Path(output_png).resolve()

    print(f"🎨 渲染中...")
    print(f"   输入: {input_path}")
    print(f"   缩放: {scale}x")

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=scale,
        )

        # 加载 HTML
        page.goto(f"file://{input_path}", wait_until="networkidle")

        # 等待 Google Fonts 加载完成
        page.wait_for_function(
            """() => document.fonts.ready.then(() => document.fonts.check('16px "Noto Sans SC"'))""",
            timeout=15000,
        )
        # 额外等待确保渲染完成
        page.wait_for_timeout(500)

        # 隐藏悬浮按钮和 toast（如果存在）
        page.evaluate("""() => {
            const fab = document.querySelector('.fab-wrap');
            const toast = document.querySelector('.export-toast');
            if (fab) fab.style.display = 'none';
            if (toast) toast.style.display = 'none';
        }""")

        # 截取 .poster 元素
        poster = page.query_selector(".poster")
        if poster:
            poster.screenshot(path=str(output_path), type="png")
        else:
            # 回退：截全页
            page.screenshot(path=str(output_path), type="png", full_page=True)

        browser.close()

    file_size = output_path.stat().st_size
    size_str = (
        f"{file_size / 1024:.0f} KB"
        if file_size < 1024 * 1024
        else f"{file_size / 1024 / 1024:.1f} MB"
    )
    print(f"✅ 导出完成: {output_path} ({size_str})")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="将视觉笔记 HTML 渲染为 PNG")
    parser.add_argument("input", help="输入 HTML 文件路径")
    parser.add_argument("output", nargs="?", default=None, help="输出 PNG 文件路径 (默认同名.png)")
    parser.add_argument("--scale", type=float, default=1.5, help="缩放倍数 (默认 1.5)")
    args = parser.parse_args()

    result = html_to_png(args.input, args.output, args.scale)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
