import pytest
from datetime import datetime, timezone
from positions import init_db, open_position, update_position, close_position, get_open_positions
from models import Position


@pytest.fixture
def conn(tmp_path):
    return init_db(str(tmp_path / "test.db"))


def _pos(**kwargs):
    defaults = dict(market_id="m1", question="Q?", side="YES",
                    entry_price=0.42, size=50.0, opened_at=datetime.now(timezone.utc))
    return Position(**{**defaults, **kwargs})


def test_open_position_returns_id(conn):
    pid = open_position(conn, _pos())
    assert pid == 1


def test_get_open_positions(conn):
    open_position(conn, _pos())
    positions = get_open_positions(conn)
    assert len(positions) == 1
    assert positions[0].side == "YES"
    assert positions[0].entry_price == 0.42


def test_update_position_calculates_pnl(conn):
    pid = open_position(conn, _pos(entry_price=0.40, size=100.0))
    update_position(conn, pid, 0.50)
    positions = get_open_positions(conn)
    assert abs(positions[0].pnl - 10.0) < 0.001
    assert positions[0].current_price == 0.50


def test_close_position_removes_from_open(conn):
    pid = open_position(conn, _pos())
    close_position(conn, pid)
    positions = get_open_positions(conn)
    assert positions == []
