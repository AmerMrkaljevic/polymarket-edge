# sources/manifold.py
from __future__ import annotations
import requests
import config
from models import Market


def fetch_markets() -> list[Market]:
    """Fetch open binary markets from Manifold Markets."""
    resp = requests.get(
        f"{config.MANIFOLD_BASE}/markets",
        params={"limit": 500},
        timeout=config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    markets = []
    for item in resp.json():
        if item.get("outcomeType") != "BINARY":
            continue
        if item.get("isResolved"):
            continue
        prob = item.get("probability")
        if prob is None:
            continue
        markets.append(Market(
            source="manifold",
            id=item["id"],
            question=item.get("question", ""),
            yes_price=float(prob),
            url=item.get("url", ""),
        ))
    return markets
