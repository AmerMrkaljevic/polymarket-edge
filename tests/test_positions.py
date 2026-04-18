import sqlite3
import pytest
from positions import init_db, open_position, update_outcome, get_closed_positions, get_open_positions
from models import Position


@pytest.fixture
def conn():
    c = init_db(":memory:")
    yield c
    c.close()


def _make_pos(**kwargs):
    defaults = dict(market_id="m1", question="Q?", side="YES", entry_price=0.5, size=10.0)
    defaults.update(kwargs)
    return Position(**defaults)


def test_outcome_column_exists(conn):
    row = conn.execute("PRAGMA table_info(positions)").fetchall()
    columns = [r["name"] for r in row]
    assert "outcome" in columns


def test_update_outcome_sets_win(conn):
    pid = open_position(conn, _make_pos())
    update_outcome(conn, pid, "win")
    row = conn.execute("SELECT outcome, status FROM positions WHERE id = ?", (pid,)).fetchone()
    assert row["outcome"] == "win"
    assert row["status"] == "closed"


def test_update_outcome_sets_loss(conn):
    pid = open_position(conn, _make_pos())
    update_outcome(conn, pid, "loss")
    row = conn.execute("SELECT outcome FROM positions WHERE id = ?", (pid,)).fetchone()
    assert row["outcome"] == "loss"


def test_get_closed_positions_returns_closed_only(conn):
    pid1 = open_position(conn, _make_pos(market_id="m1"))
    pid2 = open_position(conn, _make_pos(market_id="m2"))
    update_outcome(conn, pid1, "win")
    closed = get_closed_positions(conn)
    open_ = get_open_positions(conn)
    assert len(closed) == 1
    assert closed[0].market_id == "m1"
    assert len(open_) == 1
    assert open_[0].market_id == "m2"


def test_update_position_calculates_pnl(conn):
    pid = open_position(conn, _make_pos(entry_price=0.50, size=100.0))
    from positions import update_position
    update_position(conn, pid, 0.60)
    row = conn.execute("SELECT current_price, pnl FROM positions WHERE id = ?", (pid,)).fetchone()
    assert row["current_price"] == 0.60
    assert abs(row["pnl"] - 10.0) < 0.001  # (0.60 - 0.50) * 100.0 = 10.0


def test_close_position_sets_status_closed(conn):
    pid = open_position(conn, _make_pos())
    from positions import close_position
    close_position(conn, pid)
    row = conn.execute("SELECT status FROM positions WHERE id = ?", (pid,)).fetchone()
    assert row["status"] == "closed"
