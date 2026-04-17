from models import Market, Edge, Position
from datetime import datetime


def test_market_fields():
    m = Market(source="polymarket", id="abc", question="Will X happen?",
               yes_price=0.45, url="http://example.com")
    assert m.source == "polymarket"
    assert m.yes_price == 0.45


def test_edge_spread():
    e = Edge(type="arb", question="Q", source_a="polymarket", price_a=0.4,
             source_b="kalshi", price_b=0.55, spread=0.15)
    assert e.spread == 0.15
    assert isinstance(e.detected_at, datetime)


def test_position_defaults():
    p = Position(market_id="x", question="Q?", side="YES",
                 entry_price=0.4, size=50.0)
    assert p.status == "open"
    assert p.current_price == 0.0
    assert p.pnl == 0.0
