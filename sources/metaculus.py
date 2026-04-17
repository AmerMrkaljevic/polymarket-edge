# sources/metaculus.py
from __future__ import annotations
import requests
import config
from models import Market


def fetch_markets() -> list[Market]:
    """Fetch open forecast questions from Metaculus."""
    resp = requests.get(
        f"{config.METACULUS_BASE}/questions/",
        params={"format": "json", "type": "forecast", "status": "open", "limit": 200},
        timeout=config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    markets = []
    for item in resp.json().get("results", []):
        pred = item.get("community_prediction") or {}
        full = pred.get("full") or {}
        q2 = full.get("q2")
        if q2 is None:
            continue
        markets.append(Market(
            source="metaculus",
            id=str(item["id"]),
            question=item.get("title", ""),
            yes_price=float(q2),
            url=f"https://www.metaculus.com{item.get('page_url', '')}",
        ))
    return markets
