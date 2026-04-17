from unittest.mock import patch
from sources.metaculus import fetch_markets

_MOCK = {
    "results": [
        {"id": 1, "title": "Will X happen?",
         "community_prediction": {"full": {"q2": 0.6}}, "page_url": "/questions/1/"},
        {"id": 2, "title": "No prediction yet",
         "community_prediction": {"full": {}}},
    ]
}


def test_fetch_markets_with_prediction():
    with patch("sources.metaculus.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert len(markets) == 1
    assert markets[0].yes_price == 0.6
    assert markets[0].source == "metaculus"


def test_fetch_markets_skips_no_prediction():
    with patch("sources.metaculus.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _MOCK
        mock_get.return_value.raise_for_status = lambda: None
        markets = fetch_markets()
    assert all(m.id != "2" for m in markets)
