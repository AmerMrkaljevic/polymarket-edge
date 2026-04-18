from dashboard import render
from models import Edge, Position
from analytics import AnalyticsSummary
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


def test_render_with_no_data_does_not_crash():
    summary = AnalyticsSummary(closed_count=0, win_rate=0.0, total_pnl=0.0, max_drawdown=0.0)
    render(edges=[], positions=[], next_poll_in=60, summary=summary)


def test_render_with_summary_data_does_not_crash():
    summary = AnalyticsSummary(closed_count=10, win_rate=0.7, total_pnl=42.5, max_drawdown=-8.0)
    render(edges=[], positions=[], next_poll_in=30, summary=summary)


def test_render_without_summary_does_not_crash():
    render(edges=[], positions=[], next_poll_in=60, summary=None)
