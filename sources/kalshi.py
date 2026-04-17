from __future__ import annotations
import requests
import config
from models import Market


def fetch_markets() -> list[Market]:
    """Fetch open markets from Kalshi API. Prices are in cents (0–100)."""
    markets = []
    cursor = None

    while True:
        params: dict = {"limit": 100, "status": "open"}
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(
            f"{config.KALSHI_BASE}/markets",
            params=params,
            timeout=config.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("markets", []):
            yes_bid = item.get("yes_bid")
            yes_ask = item.get("yes_ask")
            if yes_bid is None or yes_ask is None:
                continue
            yes_price = (float(yes_bid) + float(yes_ask)) / 2 / 100
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
