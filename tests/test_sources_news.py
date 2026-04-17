from unittest.mock import patch, MagicMock
from sources.news import fetch_headlines


def _make_feed(titles):
    feed = MagicMock()
    feed.entries = [MagicMock(title=t, summary="") for t in titles]
    return feed


def test_fetch_headlines_returns_lowercased():
    with patch("sources.news.feedparser.parse") as mock_parse:
        mock_parse.return_value = _make_feed(["Breaking News: Big Event Happened"])
        headlines = fetch_headlines()
    assert any("breaking news" in h for h in headlines)


def test_fetch_headlines_handles_feed_error():
    with patch("sources.news.feedparser.parse", side_effect=Exception("network error")):
        headlines = fetch_headlines()
    assert headlines == []


def test_fetch_headlines_caps_at_20_per_feed():
    with patch("sources.news.feedparser.parse") as mock_parse:
        feed = MagicMock()
        feed.entries = [MagicMock(title=f"Headline {i}", summary="") for i in range(50)]
        mock_parse.return_value = feed
        headlines = fetch_headlines()
    # 2 feeds × 20 headlines each = 40 max
    assert len(headlines) <= 40
