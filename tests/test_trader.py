import pytest
from unittest.mock import MagicMock
from models import Edge, Position
from trader import should_trade, kelly_size, maybe_trade
from datetime import datetime, timezone


def _edge(spread=0.10, price_a=0.40, price_b=0.50, type_="arb"):
    return Edge(type=type_, question="Q?", source_a="polymarket",
                price_a=price_a, source_b="kalshi", price_b=price_b,
                spread=spread, detected_at=datetime.now(timezone.utc))


def _pos(market_id="m1", size=50.0):
    return Position(market_id=market_id, question="Q?", side="YES",
                    entry_price=0.5, size=size)


def test_kelly_size_returns_positive_for_valid_edge():
    size = kelly_size(bankroll=1000.0, spread=0.10, price=0.40, open_exposure=0.0)
    assert size > 0


def test_kelly_size_capped_at_max_position_pct():
    import config
    size = kelly_size(bankroll=1000.0, spread=0.50, price=0.10, open_exposure=0.0)
    assert size <= 1000.0 * config.MAX_POSITION_PCT


def test_kelly_size_zero_when_no_remaining_capacity():
    import config
    max_exp = 1000.0 * config.MAX_TOTAL_EXPOSURE_PCT  # 250
    size = kelly_size(bankroll=1000.0, spread=0.10, price=0.40, open_exposure=max_exp)
    assert size == 0.0


def test_maybe_trade_buys_yes_when_poly_cheaper():
    broker = MagicMock()
    broker.get_open_positions.return_value = []
    broker.place_order.return_value = "order1"
    edge = _edge(price_a=0.40, price_b=0.55)  # poly cheaper → buy YES
    result = maybe_trade(edge, broker, "market1")
    assert result == "order1"
    call_args = broker.place_order.call_args
    assert call_args[0][2] == "YES"


def test_maybe_trade_buys_no_when_poly_expensive():
    broker = MagicMock()
    broker.get_open_positions.return_value = []
    broker.place_order.return_value = "order2"
    edge = _edge(price_a=0.65, price_b=0.50)  # poly expensive → buy NO
    result = maybe_trade(edge, broker, "market1")
    assert result == "order2"
    call_args = broker.place_order.call_args
    assert call_args[0][2] == "NO"


def test_maybe_trade_skips_duplicate_position():
    broker = MagicMock()
    existing = _pos(market_id="market1")
    broker.get_open_positions.return_value = [existing]
    edge = _edge()
    result = maybe_trade(edge, broker, "market1")
    assert result is None
    broker.place_order.assert_not_called()


def test_maybe_trade_skips_news_edge():
    broker = MagicMock()
    broker.get_open_positions.return_value = []
    edge = _edge(type_="news")
    result = maybe_trade(edge, broker, "market1")
    assert result is None
