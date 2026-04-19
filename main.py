# main.py
from __future__ import annotations
import time

import config
from sources import polymarket, kalshi, manifold, metaculus, news, reddit, telegram
from sources.polymarket import fetch_prices
from matcher import match_markets, match_news
from analyzer import compute_arb_edges, compute_news_edges
from broker import get_broker
from trader import maybe_trade
from closer import check_and_close
from analytics import compute_summary
from dashboard import render
from positions import update_position


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
        all_headlines = (
            _safe_fetch(news.fetch_headlines, "news", []) +
            _safe_fetch(reddit.fetch_headlines, "reddit", []) +
            _safe_fetch(telegram.fetch_headlines, "telegram", [])
        )

        arb_pairs = match_markets(pm_markets, other_markets)
        news_pairs = match_news(pm_markets, all_headlines)
        edges = compute_arb_edges(arb_pairs) + compute_news_edges(news_pairs)

        # Precompute question → market_id for O(1) edge lookup
        question_to_id = {pm.question: pm.id for pm, _ in arb_pairs}

        # Update current prices for open positions
        open_positions = broker.get_open_positions()
        market_ids = [p.market_id for p in open_positions]
        current_prices = _safe_fetch(
            lambda: fetch_prices(market_ids), "prices", {}
        ) if market_ids else {}

        for pos in open_positions:
            if pos.market_id in current_prices:
                update_position(broker.conn, pos.id, current_prices[pos.market_id])

        # Auto-close positions that hit profit target, edge-gone, or time-stop
        check_and_close(broker, current_prices)

        # Trade edges
        for edge in edges:
            if edge.type == "arb":
                market_id = question_to_id.get(edge.question)
                if market_id:
                    maybe_trade(edge, broker, market_id)

        summary = compute_summary(broker.conn)
        positions = broker.get_open_positions()
        elapsed = time.time() - start
        next_poll_in = max(0, int(config.POLL_INTERVAL - elapsed))
        render(edges, positions, next_poll_in, summary)

        time.sleep(next_poll_in)


def _safe_fetch(fn, name: str, default):
    try:
        return fn()
    except Exception as exc:
        print(f"[warn] {name} fetch failed: {exc}")
        return default


if __name__ == "__main__":
    run()
