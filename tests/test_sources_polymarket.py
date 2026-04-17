from unittest.mock import patch
from sources.polymarket import fetch_markets

_MOCK_RESPONSE = {
    "data": [
        {
            "condition_id": "abc123",
            "question": "Will it rain tomorrow?",
            "market_slug": "rain-tomorrow",
            "tokens": [
                {"outcome": "Yes", "price": "0.42"},
                {"outcome": "No", "price": "0.58"},
            ],
        },
        {
            "condition_id": "no_yes_token",
            "question": "No yes token market",
            "tokens": [{"outcome": "No", "price": "0.5"}],
        },
    ],
    "next_cursor": "",
}


def test_fetch_markets_returns_market():
    with patch("sources.polymarket.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK_RESPONSE
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert len(markets) == 1
    assert markets[0].source == "polymarket"
    assert markets[0].yes_price == 0.42
    assert markets[0].question == "Will it rain tomorrow?"


def test_fetch_markets_skips_no_yes_token():
    with patch("sources.polymarket.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK_RESPONSE
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert all(m.id != "no_yes_token" for m in markets)
