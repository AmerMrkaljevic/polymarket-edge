from unittest.mock import patch, MagicMock
from sources.polymarket import fetch_markets, fetch_prices

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


def test_fetch_prices_returns_dict(requests_mock):
    mock_response = {
        "tokens": [
            {"outcome": "Yes", "price": "0.72"},
            {"outcome": "No",  "price": "0.28"},
        ]
    }
    requests_mock.get(
        "https://clob.polymarket.com/markets/cond123",
        json=mock_response,
    )
    result = fetch_prices(["cond123"])
    assert result == {"cond123": 0.72}


def test_fetch_prices_skips_failed_ids(requests_mock):
    requests_mock.get(
        "https://clob.polymarket.com/markets/bad_id",
        status_code=404,
    )
    result = fetch_prices(["bad_id"])
    assert result == {}


def test_fetch_markets_populates_volume(requests_mock):
    requests_mock.get(
        "https://clob.polymarket.com/markets",
        json={
            "data": [{
                "condition_id": "c1",
                "question": "Test?",
                "market_slug": "test",
                "volume": "12345.67",
                "tokens": [{"outcome": "Yes", "price": "0.6"}, {"outcome": "No", "price": "0.4"}],
            }],
            "next_cursor": "LTE=",
        },
    )
    markets = fetch_markets()
    assert len(markets) == 1
    assert markets[0].volume == 12345.67
