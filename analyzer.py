# analyzer.py
from __future__ import annotations
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config
from models import Market, Edge

_vader = SentimentIntensityAnalyzer()


def compute_arb_edges(pairs: list[tuple[Market, Market]]) -> list[Edge]:
    """Compute arbitrage edges. High-volume markets get a 20% ranking bonus."""
    edges = []
    for pm, other in pairs:
        spread = abs(pm.yes_price - other.yes_price)
        if spread < config.MIN_EDGE_SIZE:
            continue
        rank_spread = spread * (1.2 if pm.volume > 10_000 else 1.0)
        edges.append((rank_spread, Edge(
            type="arb",
            question=pm.question,
            source_a=pm.source,
            price_a=pm.yes_price,
            source_b=other.source,
            price_b=other.yes_price,
            spread=spread,
            detected_at=datetime.now(timezone.utc),
        )))
    return [e for _, e in sorted(edges, key=lambda x: x[0], reverse=True)]


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
    """Return 0.0–1.0 sentiment using VADER (0.5 = neutral)."""
    compound = _vader.polarity_scores(text)["compound"]  # -1.0 to +1.0
    return (compound + 1.0) / 2.0
