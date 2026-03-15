from _src.links import extract_urls
from _src.registry import CrawlerRegistry
from _src.router import extract_domain, normalize_url


def test_normalize_url_strips_www_and_sorts_query():
    normalized = normalize_url("https://www.example.com/page/?b=2&a=1#frag")
    assert normalized == "https://example.com/page?a=1&b=2"


def test_extract_domain():
    assert extract_domain("https://www.reddit.com/r/python/comments/123") == "reddit.com"


def test_extract_urls_preserves_order_and_deduplicates():
    text = "See https://example.com/a and https://example.com/a, then https://news.ycombinator.com/item?id=1."
    assert extract_urls(text) == [
        "https://example.com/a",
        "https://news.ycombinator.com/item?id=1",
    ]


def test_registry_matches_specific_crawler_and_fallback():
    registry = CrawlerRegistry()
    assert registry.match("https://news.ycombinator.com/item?id=123").id == "hackernews"
    assert registry.match("https://www.zhihu.com/question/610072126").id == "zhihu"
    assert registry.match("https://x.com/openai/status/1234567890").id == "x"
    assert registry.match("https://www.xiaohongshu.com/explore/65f1d5f70000000001020304").id == "xiaohongshu"
    assert registry.match("https://m.weibo.cn/detail/5123456789012345").id == "weibo"
    assert registry.match("https://example.com/articles/hello").id == "generic_html"
