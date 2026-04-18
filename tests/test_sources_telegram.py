import pytest
from unittest.mock import patch
from sources.telegram import fetch_headlines


_FAKE_HTML = """
<html><body>
<div class="tgme_widget_message_text">Breaking: Markets react to news</div>
<div class="tgme_widget_message_text">Polymarket whale buys YES on election</div>
</body></html>
"""


def test_fetch_headlines_parses_messages(requests_mock):
    import config
    for ch in config.TELEGRAM_CHANNELS:
        requests_mock.get(f"https://t.me/s/{ch}", text=_FAKE_HTML)
    headlines = fetch_headlines()
    assert isinstance(headlines, list)
    assert all(isinstance(h, str) for h in headlines)
    assert len(headlines) == len(config.TELEGRAM_CHANNELS) * 2


def test_fetch_headlines_handles_failed_channel(requests_mock):
    import config
    for ch in config.TELEGRAM_CHANNELS:
        requests_mock.get(f"https://t.me/s/{ch}", status_code=403)
    headlines = fetch_headlines()
    assert headlines == []
