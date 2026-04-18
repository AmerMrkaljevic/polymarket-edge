# closer.py
from __future__ import annotations
from datetime import datetime, timezone
import config
from positions import update_outcome


def check_and_close(broker, current_prices: dict[str, float]) -> None:
    """Check all open positions against exit conditions and close if triggered."""
    for pos in broker.get_open_positions():
        # Only check edge_gone if we have actual price data
        has_price = pos.market_id in current_prices
        current = current_prices.get(pos.market_id, pos.entry_price)
        pnl_pct = (current - pos.entry_price) / pos.entry_price if pos.entry_price > 0 else 0.0
        age_days = (datetime.now(timezone.utc) - pos.opened_at).days

        profit_hit = pnl_pct >= config.PROFIT_TARGET
        edge_gone = has_price and abs(pnl_pct) < config.CLOSE_EDGE_THRESHOLD
        time_stop = age_days >= config.POSITION_TIME_STOP_DAYS

        if profit_hit or edge_gone or time_stop:
            outcome = "win" if pnl_pct >= 0 else "loss"
            update_outcome(broker.conn, pos.id, outcome)
