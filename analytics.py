# analytics.py
from __future__ import annotations
from dataclasses import dataclass
import sqlite3
from positions import get_closed_positions


@dataclass
class AnalyticsSummary:
    closed_count: int
    win_rate: float       # 0.0–1.0
    total_pnl: float      # USDC
    max_drawdown: float   # largest single losing trade (negative number or 0)


def compute_summary(conn: sqlite3.Connection) -> AnalyticsSummary:
    closed = get_closed_positions(conn)
    if not closed:
        return AnalyticsSummary(closed_count=0, win_rate=0.0, total_pnl=0.0, max_drawdown=0.0)

    wins = sum(1 for p in closed if p.outcome == "win")
    win_rate = wins / len(closed)
    total_pnl = sum(p.pnl for p in closed)
    losses = [p.pnl for p in closed if p.pnl < 0]
    max_drawdown = min(losses) if losses else 0.0

    return AnalyticsSummary(
        closed_count=len(closed),
        win_rate=win_rate,
        total_pnl=total_pnl,
        max_drawdown=max_drawdown,
    )
