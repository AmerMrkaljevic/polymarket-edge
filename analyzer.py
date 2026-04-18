# analyzer.py
from __future__ import annotations
from datetime import datetime, timezone
import config
from models import Market, Edge

_POSITIVE = {"win", "lead", "surge", "rise", "approve", "pass", "beat",
             "gain", "up", "high", "bullish", "confirm", "leads"}
_NEGATIVE = {"lose", "fall", "drop", "fail", "reject", "crash", "down",
             "low", "bearish", "deny", "suspend", "loss"}


def compute_arb_edges(pairs: list[tuple[Market, Market]]) -> list[Edge]:
    """Compute arbitrage edges from matched (polymarket, other) pairs."""
    edges = []
    for pm, other in pairs:
        spread = abs(pm.yes_price - other.yes_price)
        if spread < config.MIN_EDGE_SIZE:
            continue
        edges.append(Edge(
            type="arb",
            question=pm.question,
            source_a=pm.source,
            price_a=pm.yes_price,
            source_b=other.source,
            price_b=other.yes_price,
            spread=spread,
            detected_at=datetime.now(timezone.utc),
        ))
    return sorted(edges, key=lambda e: e.spread, reverse=True)


def compute_news_edges(news_pairs: list[tuple[Market, str]]) -> list[Edge]:
    """Create news-sentiment edges for markets with matching headlines."""
    edges = []
    for pm, headline in news_pairs:
        sentiment = _sentiment_score(headline)
        edges.append(Edge(
            type="news",
            question=pm.question,
            source_a=pm.source,
            price_a=pm.yes_price,
            source_b="news",
            price_b=sentiment,
            spread=abs(pm.yes_price - sentiment),
            detected_at=datetime.now(timezone.utc),
        ))
    return sorted(edges, key=lambda e: e.spread, reverse=True)


def _sentiment_score(text: str) -> float:
    """Return 0.0–1.0 sentiment based on positive/negative keyword count."""
    words = text.lower().split()
    pos = sum(1 for w in words if w in _POSITIVE)
    neg = sum(1 for w in words if w in _NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.5
    return pos / total
