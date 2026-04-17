from unittest.mock import patch
from sources.manifold import fetch_markets

_MOCK = [
    {"id": "m1", "question": "Will AI surpass human?", "outcomeType": "BINARY",
     "probability": 0.35, "url": "https://manifold.markets/m/m1"},
    {"id": "m2", "question": "Multi-choice market", "outcomeType": "MULTIPLE_CHOICE",
     "probability": None, "url": ""},
]


def test_fetch_markets_binary_only():
    with patch("sources.manifold.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert len(markets) == 1
    assert markets[0].yes_price == 0.35
    assert markets[0].source == "manifold"


def test_fetch_markets_skips_no_probability():
    with patch("sources.manifold.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert all(m.id != "m2" for m in markets)
