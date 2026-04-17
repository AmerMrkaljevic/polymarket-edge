from __future__ import annotations
import requests
import config
from models import Market


def fetch_markets() -> list[Market]:
    """Fetch active binary markets from Polymarket CLOB API."""
    markets = []
    next_cursor = ""

    while True:
        params = {"next_cursor": next_cursor} if next_cursor else {}
        resp = requests.get(
            f"{config.POLYMARKET_HOST}/markets",
            params=params,
            timeout=config.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("data", []):
            yes_price = _extract_yes_price(item.get("tokens", []))
            if yes_price is None:
                continue
            markets.append(Market(
                source="polymarket",
                id=item["condition_id"],
                question=item.get("question", ""),
                yes_price=yes_price,
                url=f"https://polymarket.com/event/{item.get('market_slug', item['condition_id'])}",
            ))

        next_cursor = data.get("next_cursor", "")
        if not next_cursor or next_cursor == "LTE=":
            break
        if len(markets) >= 500:
            break

    return markets


def _extract_yes_price(tokens: list[dict]) -> float | None:
    for t in tokens:
        if t.get("outcome", "").lower() == "yes":
            price = t.get("price")
            if price is not None:
                return float(price)
    return None
