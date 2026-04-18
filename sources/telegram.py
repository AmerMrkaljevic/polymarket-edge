# sources/telegram.py
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import config


def fetch_headlines() -> list[str]:
    """Fetch recent messages from public Telegram channels (no API key required)."""
    headlines = []
    for channel in config.TELEGRAM_CHANNELS:
        try:
            resp = requests.get(
                f"https://t.me/s/{channel}",
                timeout=config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for msg in soup.select(".tgme_widget_message_text")[:20]:
                text = msg.get_text(" ", strip=True)
                if text:
                    headlines.append(text)
        except Exception:
            pass
    return headlines
