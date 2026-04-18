import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
from models import Position
from closer import check_and_close


def _pos(market_id="m1", entry_price=0.50, size=50.0, days_old=0, id=1):
    opened = datetime.now(timezone.utc) - timedelta(days=days_old)
    return Position(market_id=market_id, question="Q?", side="YES",
                    entry_price=entry_price, size=size, opened_at=opened, id=id)


def test_close_at_profit_target():
    broker = MagicMock()
    pos = _pos(entry_price=0.50)
    broker.get_open_positions.return_value = [pos]
    current_prices = {"m1": 0.56}  # +12% > PROFIT_TARGET 10%
    with patch("closer.update_outcome") as mock_outcome:
        check_and_close(broker, current_prices)
        mock_outcome.assert_called_once_with(broker.conn, 1, "win")


def test_close_when_edge_gone():
    broker = MagicMock()
    pos = _pos(entry_price=0.50)
    broker.get_open_positions.return_value = [pos]
    current_prices = {"m1": 0.505}  # +1% spread gone, < CLOSE_EDGE_THRESHOLD 2%
    with patch("closer.update_outcome") as mock_outcome:
        check_and_close(broker, current_prices)
        mock_outcome.assert_called_once_with(broker.conn, 1, "win")


def test_close_on_time_stop():
    broker = MagicMock()
    pos = _pos(entry_price=0.50, days_old=8)  # 8 days old > POSITION_TIME_STOP_DAYS 7
    broker.get_open_positions.return_value = [pos]
    current_prices = {"m1": 0.45}  # losing position, closed due to time stop
    with patch("closer.update_outcome") as mock_outcome:
        check_and_close(broker, current_prices)
        mock_outcome.assert_called_once_with(broker.conn, 1, "loss")


def test_no_close_when_position_still_active():
    broker = MagicMock()
    pos = _pos(entry_price=0.50, days_old=1)
    broker.get_open_positions.return_value = [pos]
    current_prices = {"m1": 0.53}  # +6%, not at profit target yet
    with patch("closer.update_outcome") as mock_outcome:
        check_and_close(broker, current_prices)
        mock_outcome.assert_not_called()


def test_uses_entry_price_when_no_current_price():
    broker = MagicMock()
    pos = _pos(entry_price=0.50, days_old=1)
    broker.get_open_positions.return_value = [pos]
    current_prices = {}  # no price data for this market
    with patch("closer.update_outcome") as mock_outcome:
        check_and_close(broker, current_prices)
        mock_outcome.assert_not_called()  # 0% pnl, not at target, not expired
