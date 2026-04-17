# sources/news.py
from __future__ import annotations
import feedparser
import config


def fetch_headlines() -> list[str]:
    """Fetch recent headlines from configured RSS feeds. Returns lowercased strings."""
    headlines = []
    for feed_url in config.NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                headlines.append(f"{title} {summary}".lower())
        except Exception:
            continue
    return headlines
