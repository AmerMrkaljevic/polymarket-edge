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
