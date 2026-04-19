from unittest.mock import patch
from sources.kalshi import fetch_markets

_MOCK_RESPONSE = {
    "markets": [
        {
            "ticker": "FED-2024-CUT",
            "title": "Will the Fed cut rates in 2024?",
            "yes_bid_dollars": 0.55,
            "yes_ask_dollars": 0.57,
        },
        {
            "ticker": "NO-PRICES",
            "title": "Market with no prices",
            "yes_bid_dollars": None,
            "yes_ask_dollars": None,
        },
    ],
    "cursor": None,
}


def test_fetch_markets_returns_market():
    with patch("sources.kalshi.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK_RESPONSE
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert len(markets) == 1
    assert markets[0].source == "kalshi"
    assert abs(markets[0].yes_price - 0.56) < 0.001  # (0.55+0.57)/2
    assert markets[0].question == "Will the Fed cut rates in 2024?"


def test_fetch_markets_skips_missing_prices():
    with patch("sources.kalshi.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK_RESPONSE
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert all(m.id != "NO-PRICES" for m in markets)
