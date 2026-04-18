# main.py
from __future__ import annotations
import time

import config
from sources import polymarket, kalshi, manifold, metaculus, news
from matcher import match_markets, match_news
from analyzer import compute_arb_edges, compute_news_edges
from broker import get_broker
from trader import maybe_trade
from dashboard import render


def run() -> None:
    broker = get_broker()

    while True:
        start = time.time()

        pm_markets = _safe_fetch(polymarket.fetch_markets, "polymarket", [])
        other_markets = (
            _safe_fetch(kalshi.fetch_markets, "kalshi", []) +
            _safe_fetch(manifold.fetch_markets, "manifold", []) +
            _safe_fetch(metaculus.fetch_markets, "metaculus", [])
        )
        headlines = _safe_fetch(news.fetch_headlines, "news", [])

        arb_pairs = match_markets(pm_markets, other_markets)
        news_pairs = match_news(pm_markets, headlines)
        edges = compute_arb_edges(arb_pairs) + compute_news_edges(news_pairs)

        for edge in edges:
            if edge.type == "arb":
                market_id = next(
                    (pm.id for pm, _ in arb_pairs if pm.question == edge.question),
                    None,
                )
                if market_id:
                    maybe_trade(edge, broker, market_id)

        positions = broker.get_open_positions()
        elapsed = time.time() - start
        next_poll_in = max(0, int(config.POLL_INTERVAL - elapsed))
        render(edges, positions, next_poll_in)

        time.sleep(next_poll_in)


def _safe_fetch(fn, name: str, default):
    try:
        return fn()
    except Exception as exc:
        print(f"[warn] {name} fetch failed: {exc}")
        return default


if __name__ == "__main__":
    run()
