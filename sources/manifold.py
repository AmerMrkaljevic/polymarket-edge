# sources/manifold.py
from __future__ import annotations
import time
import requests
import config
from models import Market

_NOW_MS = lambda: int(time.time() * 1000)


def fetch_markets() -> list[Market]:
    """Fetch open binary markets from Manifold Markets that haven't closed yet."""
    resp = requests.get(
        f"{config.MANIFOLD_BASE}/markets",
        params={"limit": 500},
        timeout=config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    now_ms = _NOW_MS()
    markets = []
    for item in resp.json():
        if item.get("outcomeType") != "BINARY":
            continue
        if item.get("isResolved"):
            continue
        # skip markets whose close time has already passed
        close_time = item.get("closeTime")
        if close_time and int(close_time) < now_ms:
            continue
        prob = item.get("probability")
        if prob is None:
            continue
        # skip near-resolved markets (price essentially at 0 or 1)
        if float(prob) < 0.02 or float(prob) > 0.98:
            continue
        markets.append(Market(
            source="manifold",
            id=item["id"],
            question=item.get("question", ""),
            yes_price=float(prob),
            url=item.get("url", ""),
        ))
    return markets
