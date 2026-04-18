import pytest
from broker import PaperBroker


@pytest.fixture
def broker(tmp_path):
    return PaperBroker(db_path=str(tmp_path / "test.db"))


def test_place_order_returns_id(broker):
    order_id = broker.place_order("m1", "Will X happen?", "YES", 0.42, 50.0)
    assert order_id == "1"


def test_get_open_positions_after_order(broker):
    broker.place_order("m1", "Will X happen?", "YES", 0.42, 50.0)
    positions = broker.get_open_positions()
    assert len(positions) == 1
    assert positions[0].side == "YES"
    assert positions[0].entry_price == 0.42


def test_close_order_removes_position(broker):
    order_id = broker.place_order("m1", "Q?", "YES", 0.4, 50.0)
    result = broker.close_order(order_id)
    assert result is True
    assert broker.get_open_positions() == []


def test_multiple_orders(broker):
    broker.place_order("m1", "Q1?", "YES", 0.4, 25.0)
    broker.place_order("m2", "Q2?", "YES", 0.6, 25.0)
    assert len(broker.get_open_positions()) == 2
