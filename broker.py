# broker.py
from __future__ import annotations
import os
from datetime import datetime, timezone
import config
from models import Position
from positions import init_db, open_position, get_open_positions, close_position


class PaperBroker:
    def __init__(self, db_path: str = config.DB_PATH):
        self.conn = init_db(db_path)

    def place_order(
        self, market_id: str, question: str, side: str, price: float, size: float
    ) -> str:
        pos = Position(
            market_id=market_id,
            question=question,
            side=side,
            entry_price=price,
            size=size,
            opened_at=datetime.now(timezone.utc),
        )
        pid = open_position(self.conn, pos)
        return str(pid)

    def get_open_positions(self) -> list[Position]:
        return get_open_positions(self.conn)

    def close_order(self, order_id: str) -> bool:
        close_position(self.conn, int(order_id))
        return True


class LiveBroker:
    """Real Polymarket trading via py-clob-client. Requires env vars set from .env."""

    def __init__(self, db_path: str = config.DB_PATH):
        from py_clob_client.client import ClobClient
        self._client = ClobClient(
            host=config.POLYMARKET_HOST,
            key=os.environ["POLYMARKET_PRIVATE_KEY"],
            chain_id=137,
            creds={
                "apiKey": os.environ["POLYMARKET_API_KEY"],
                "secret": os.environ["POLYMARKET_API_SECRET"],
                "passphrase": os.environ["POLYMARKET_API_PASSPHRASE"],
            },
        )
        self.conn = init_db(db_path)

    def place_order(
        self, market_id: str, question: str, side: str, price: float, size: float
    ) -> str:
        from py_clob_client.clob_types import OrderArgs, BUY
        order_args = OrderArgs(token_id=market_id, price=price, size=size, side=BUY)
        resp = self._client.create_and_post_order(order_args)
        order_id = resp.get("orderID", "unknown")
        pos = Position(
            market_id=market_id,
            question=question,
            side=side,
            entry_price=price,
            size=size,
            opened_at=datetime.now(timezone.utc),
        )
        open_position(self.conn, pos)
        return order_id

    def get_open_positions(self) -> list[Position]:
        return get_open_positions(self.conn)

    def close_order(self, order_id: str) -> bool:
        self._client.cancel(order_id)
        return True


def get_broker(db_path: str = config.DB_PATH) -> PaperBroker | LiveBroker:
    if config.PAPER_TRADING:
        return PaperBroker(db_path)
    _confirm_live_mode()
    return LiveBroker(db_path)


def _confirm_live_mode() -> None:
    print("\n⚠  WARNING: LIVE TRADING MODE ACTIVE. Real money will be used.")
    answer = input("Type CONFIRM to proceed: ")
    if answer.strip() != "CONFIRM":
        raise SystemExit("Aborted.")
