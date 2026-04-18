from unittest.mock import MagicMock
from trader import should_trade, compute_size, maybe_trade
from models import Edge, Position
from datetime import datetime, timezone


def _edge(spread=0.10, type="arb", price_a=0.40, price_b=0.50):
    return Edge(type=type, question="Q?", source_a="polymarket", price_a=price_a,
                source_b="kalshi", price_b=price_b, spread=spread,
                detected_at=datetime.now(timezone.utc))


def test_should_trade_passes_valid_edge():
    assert should_trade(_edge(), open_exposure=0.0) is True


def test_should_trade_rejects_small_spread():
    assert should_trade(_edge(spread=0.02), open_exposure=0.0) is False


def test_should_trade_rejects_news_edge():
    assert should_trade(_edge(type="news"), open_exposure=0.0) is False


def test_should_trade_rejects_over_exposure():
    # BANKROLL=1000, MAX_TOTAL_EXPOSURE_PCT=0.25 → max=250
    assert should_trade(_edge(), open_exposure=250.0) is False


def test_compute_size_normal():
    size = compute_size(bankroll=1000.0, open_exposure=0.0)
    assert size == 50.0  # 1000 * MAX_POSITION_PCT(0.05)


def test_compute_size_limited_by_remaining_capacity():
    # 225 exposed, max=250, remaining=25 < 50
    size = compute_size(bankroll=1000.0, open_exposure=225.0)
    assert size == 25.0


def test_maybe_trade_places_order_and_returns_id():
    broker = MagicMock()
    broker.get_open_positions.return_value = []
    broker.place_order.return_value = "order-123"
    result = maybe_trade(_edge(), broker, "market-token-id")
    assert result == "order-123"
    broker.place_order.assert_called_once()


def test_maybe_trade_skips_news_edge():
    broker = MagicMock()
    broker.get_open_positions.return_value = []
    result = maybe_trade(_edge(type="news"), broker, "market-token-id")
    assert result is None
    broker.place_order.assert_not_called()


def test_maybe_trade_buys_yes_when_polymarket_underpriced():
    broker = MagicMock()
    broker.get_open_positions.return_value = []
    broker.place_order.return_value = "order-1"
    # price_a=0.40 < price_b=0.55 → buy YES (polymarket is underpriced)
    maybe_trade(_edge(price_a=0.40, price_b=0.55), broker, "mid")
    _, _, side, _, _ = broker.place_order.call_args[0]
    assert side == "YES"
