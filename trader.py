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


def kelly_size(bankroll: float, spread: float, price: float, open_exposure: float) -> float:
    """Compute order size using quarter-Kelly criterion, capped by position and exposure limits."""
    if price <= 0 or price >= 1:
        return 0.0
    # Kelly formula: f = (b*p - q) / b
    # where b = net odds (payout per unit risked), p = estimated win prob, q = 1-p
    p = min(price + spread, 0.99)
    q = 1.0 - p
    b = (1.0 - price) / price  # net odds for a binary bet at this price
    kelly_f = (b * p - q) / b
    kelly_f = max(0.0, kelly_f) * config.KELLY_FRACTION
    raw = bankroll * kelly_f
    capped = min(raw, bankroll * config.MAX_POSITION_PCT)
    remaining = (bankroll * config.MAX_TOTAL_EXPOSURE_PCT) - open_exposure
    return min(capped, max(0.0, remaining))


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

    # Deduplication: skip if we already hold a position in this market
    if any(p.market_id == market_id for p in positions):
        return None

    # Buy the underpriced side on Polymarket
    if edge.price_a < edge.price_b:
        side = "YES"
        price = edge.price_a
    else:
        side = "NO"
        price = 1.0 - edge.price_a  # NO price is complement of YES price

    size = kelly_size(config.BANKROLL, edge.spread, price, open_exposure)
    if size <= 0:
        return None

    return broker.place_order(market_id, edge.question, side, price, size)
