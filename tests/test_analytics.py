import pytest
from positions import init_db, open_position, update_outcome
from models import Position
from analytics import compute_summary


@pytest.fixture
def conn():
    c = init_db(":memory:")
    yield c
    c.close()


def _make_pos(market_id="m1"):
    from datetime import datetime, timezone
    return Position(market_id=market_id, question="Q?", side="YES",
                    entry_price=0.5, size=50.0)


def test_compute_summary_empty_db(conn):
    summary = compute_summary(conn)
    assert summary.closed_count == 0
    assert summary.win_rate == 0.0
    assert summary.total_pnl == 0.0
    assert summary.max_drawdown == 0.0


def test_compute_summary_win_rate(conn):
    for i, (outcome, pnl_adj) in enumerate([("win", 5.0), ("win", 3.0), ("loss", -4.0)]):
        pid = open_position(conn, _make_pos(market_id=f"m{i}"))
        conn.execute("UPDATE positions SET pnl = ? WHERE id = ?", (pnl_adj, pid))
        conn.commit()
        update_outcome(conn, pid, outcome)
    summary = compute_summary(conn)
    assert summary.closed_count == 3
    assert abs(summary.win_rate - 2/3) < 0.01
    assert abs(summary.total_pnl - 4.0) < 0.01


def test_compute_summary_max_drawdown(conn):
    for i, (outcome, pnl_adj) in enumerate([("loss", -10.0), ("loss", -3.0), ("win", 8.0)]):
        pid = open_position(conn, _make_pos(market_id=f"m{i}"))
        conn.execute("UPDATE positions SET pnl = ? WHERE id = ?", (pnl_adj, pid))
        conn.commit()
        update_outcome(conn, pid, outcome)
    summary = compute_summary(conn)
    assert summary.max_drawdown == -10.0
