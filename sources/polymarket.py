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
            # skip near-resolved markets (price essentially 0 or 1)
            if yes_price < 0.02 or yes_price > 0.98:
                continue
            markets.append(Market(
                source="polymarket",
                id=item["condition_id"],
                question=item.get("question", ""),
                yes_price=yes_price,
                url=f"https://polymarket.com/event/{item.get('market_slug', item['condition_id'])}",
                volume=float(item.get("volume", 0) or 0),
            ))

        next_cursor = data.get("next_cursor", "")
        if not next_cursor or next_cursor == "LTE=":
            break
        if len(markets) >= 500:
            break

    return markets


def fetch_prices(market_ids: list[str]) -> dict[str, float]:
    """Fetch current YES price for each market_id. Skips failures silently."""
    prices = {}
    for mid in market_ids:
        try:
            resp = requests.get(
                f"{config.POLYMARKET_HOST}/markets/{mid}",
                timeout=config.REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            item = resp.json()
            price = _extract_yes_price(item.get("tokens", []))
            if price is not None:
                prices[mid] = price
        except Exception:
            pass
    return prices


def _extract_yes_price(tokens: list[dict]) -> float | None:
    for t in tokens:
        if t.get("outcome", "").lower() == "yes":
            price = t.get("price")
            if price is not None:
                return float(price)
    return None
