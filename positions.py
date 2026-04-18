# positions.py
from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
import config
from models import Position

_CREATE = """
CREATE TABLE IF NOT EXISTS positions (
    id            INTEGER PRIMARY KEY,
    market_id     TEXT NOT NULL,
    question      TEXT NOT NULL,
    side          TEXT NOT NULL,
    entry_price   REAL NOT NULL,
    size          REAL NOT NULL,
    current_price REAL DEFAULT 0.0,
    pnl           REAL DEFAULT 0.0,
    opened_at     TEXT NOT NULL,
    status        TEXT DEFAULT 'open'
);
"""


def init_db(path: str = config.DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE)
    conn.commit()
    return conn


def open_position(conn: sqlite3.Connection, pos: Position) -> int:
    cur = conn.execute(
        """INSERT INTO positions
           (market_id, question, side, entry_price, size, current_price, pnl, opened_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (pos.market_id, pos.question, pos.side, pos.entry_price, pos.size,
         pos.current_price, pos.pnl, pos.opened_at.isoformat(), pos.status),
    )
    conn.commit()
    return cur.lastrowid


def update_position(conn: sqlite3.Connection, position_id: int, current_price: float) -> None:
    row = conn.execute(
        "SELECT entry_price, size FROM positions WHERE id = ?", (position_id,)
    ).fetchone()
    if not row:
        return
    pnl = (current_price - row["entry_price"]) * row["size"]
    conn.execute(
        "UPDATE positions SET current_price = ?, pnl = ? WHERE id = ?",
        (current_price, pnl, position_id),
    )
    conn.commit()


def close_position(conn: sqlite3.Connection, position_id: int) -> None:
    conn.execute("UPDATE positions SET status = 'closed' WHERE id = ?", (position_id,))
    conn.commit()


def get_open_positions(conn: sqlite3.Connection) -> list[Position]:
    rows = conn.execute("SELECT * FROM positions WHERE status = 'open'").fetchall()
    return [_row_to_position(r) for r in rows]


def _row_to_position(row: sqlite3.Row) -> Position:
    return Position(
        id=row["id"],
        market_id=row["market_id"],
        question=row["question"],
        side=row["side"],
        entry_price=row["entry_price"],
        size=row["size"],
        current_price=row["current_price"],
        pnl=row["pnl"],
        opened_at=datetime.fromisoformat(row["opened_at"]),
        status=row["status"],
    )
