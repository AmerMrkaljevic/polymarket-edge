from dashboard import render
from models import Edge, Position
from datetime import datetime, timezone


def _edge():
    return Edge(type="arb", question="Will X happen?", source_a="polymarket",
                price_a=0.42, source_b="kalshi", price_b=0.57, spread=0.15,
                detected_at=datetime.now(timezone.utc))


def _pos():
    return Position(market_id="m1", question="Will X happen?", side="YES",
                    entry_price=0.42, size=50.0, current_price=0.50, pnl=4.0,
                    opened_at=datetime.now(timezone.utc))


def test_render_does_not_crash():
    render([_edge()], [_pos()], next_poll_in=45)


def test_render_empty_lists():
    render([], [], next_poll_in=60)


def test_render_news_edge():
    news_edge = Edge(type="news", question="Will X happen?", source_a="polymarket",
                     price_a=0.3, source_b="news", price_b=0.8, spread=0.5,
                     detected_at=datetime.now(timezone.utc))
    render([news_edge], [], next_poll_in=30)
