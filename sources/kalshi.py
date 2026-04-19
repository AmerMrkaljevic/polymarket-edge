from __future__ import annotations
import time
import requests
import config
from models import Market

_RETRY_DELAYS = [2, 5, 10]  # seconds between retries on 429


def _get_with_retry(url: str, params: dict) -> requests.Response:
    """GET with exponential backoff on 429 rate limit."""
    for attempt, delay in enumerate([0] + _RETRY_DELAYS):
        if delay:
            time.sleep(delay)
        resp = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
        if resp.status_code != 429:
            resp.raise_for_status()
            return resp
    resp.raise_for_status()
    return resp


def fetch_markets() -> list[Market]:
    """Fetch open markets from Kalshi elections API."""
    markets = []
    cursor = None

    while True:
        params: dict = {"limit": 100, "status": "open"}
        if cursor:
            params["cursor"] = cursor
        resp = _get_with_retry(f"{config.KALSHI_BASE}/markets", params)
        data = resp.json()

        for item in data.get("markets", []):
            yes_bid = float(item.get("yes_bid_dollars") or 0)
            yes_ask = float(item.get("yes_ask_dollars") or 0)
            if yes_bid <= 0 and yes_ask <= 0:
                continue
            # prices are already in 0-1 range (dollars)
            yes_price = (yes_bid + yes_ask) / 2 if yes_bid > 0 else yes_ask
            if yes_price < 0.02 or yes_price > 0.98:
                continue
            markets.append(Market(
                source="kalshi",
                id=item["ticker"],
                question=item.get("title", ""),
                yes_price=yes_price,
                url=f"https://kalshi.com/markets/{item['ticker']}",
            ))

        cursor = data.get("cursor")
        if not cursor or len(markets) >= 500:
            break

    return markets
