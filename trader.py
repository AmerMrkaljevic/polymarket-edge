# trader.py
from __future__ import annotations
import config
from models import Edge
from broker import PaperBroker, LiveBroker


def should_trade(edge: Edge, open_exposure: float) -> bool:
    """Return True if the edge passes risk checks and is worth trading."""
    if edge.type != "arb":
        return False
    if edge.spread < config.MIN_EDGE_SIZE:
        return False
    max_exposure = config.BANKROLL * config.MAX_TOTAL_EXPOSURE_PCT
    if open_exposure >= max_exposure:
        return False
    return True


def compute_size(bankroll: float, open_exposure: float) -> float:
    """Compute order size in USDC, capped by per-position and total exposure limits."""
    max_position = bankroll * config.MAX_POSITION_PCT
    remaining = (bankroll * config.MAX_TOTAL_EXPOSURE_PCT) - open_exposure
    return min(max_position, max(0.0, remaining))


def maybe_trade(
    edge: Edge,
    broker: PaperBroker | LiveBroker,
    market_id: str,
) -> str | None:
    """Place an order if edge passes risk checks. Returns order_id or None."""
    positions = broker.get_open_positions()
    open_exposure = sum(p.size for p in positions)

    if not should_trade(edge, open_exposure):
        return None

    size = compute_size(config.BANKROLL, open_exposure)
    if size <= 0:
        return None

    # Buy the underpriced side on Polymarket
    side = "YES" if edge.price_a < edge.price_b else "NO"
    return broker.place_order(market_id, edge.question, side, edge.price_a, size)
