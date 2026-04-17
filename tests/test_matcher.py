from matcher import match_markets, match_news
from models import Market


def _make(source, question, price=0.5):
    return Market(source=source, id="x", question=question, yes_price=price, url="")


def test_match_markets_finds_similar():
    pm = [_make("polymarket", "Will the Fed cut rates in 2024?")]
    others = [_make("kalshi", "Will the Federal Reserve cut rates in 2024?")]
    pairs = match_markets(pm, others)
    assert len(pairs) == 1
    assert pairs[0][0].source == "polymarket"
    assert pairs[0][1].source == "kalshi"


def test_match_markets_ignores_dissimilar():
    pm = [_make("polymarket", "Will Bitcoin reach 100k?")]
    others = [_make("kalshi", "Will it rain tomorrow in Paris?")]
    pairs = match_markets(pm, others)
    assert pairs == []


def test_match_markets_returns_polymarket_first():
    pm = [_make("polymarket", "Will Trump win 2024?")]
    others = [_make("manifold", "Will Donald Trump win the 2024 election?")]
    pairs = match_markets(pm, others)
    assert len(pairs) == 1
    assert pairs[0][0].source == "polymarket"


def test_match_news_finds_keyword_match():
    pm = [_make("polymarket", "Will Trump win the 2024 election?")]
    headlines = ["trump leads polls ahead 2024 election race"]
    pairs = match_news(pm, headlines)
    assert len(pairs) == 1
    assert pairs[0][0].source == "polymarket"


def test_match_news_ignores_few_keywords():
    pm = [_make("polymarket", "Will Trump win the 2024 election?")]
    headlines = ["stock market news today"]
    pairs = match_news(pm, headlines)
    assert pairs == []
