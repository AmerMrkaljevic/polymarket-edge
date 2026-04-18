# sources/reddit.py
from __future__ import annotations
import requests
import config


def fetch_headlines() -> list[str]:
    """Fetch post titles from configured subreddits using Reddit's public JSON API."""
    headlines = []
    headers = {"User-Agent": "polymarket-edge/2.0"}
    for sub in config.REDDIT_SUBREDDITS:
        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub}/hot.json",
                params={"limit": 25},
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            for post in resp.json()["data"]["children"]:
                headlines.append(post["data"]["title"])
        except Exception:
            pass
    return headlines
