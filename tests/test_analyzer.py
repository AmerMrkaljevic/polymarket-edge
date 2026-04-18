from analyzer import compute_arb_edges, compute_news_edges, _sentiment_score
from models import Market, Edge
from datetime import datetime


def _market(source, question, price):
    return Market(source=source, id="x", question=question, yes_price=price, url="")


def test_compute_arb_edges_detects_spread():
    pm = _market("polymarket", "Will X happen?", 0.40)
    ks = _market("kalshi", "Will X happen?", 0.55)
    edges = compute_arb_edges([(pm, ks)])
    assert len(edges) == 1
    assert abs(edges[0].spread - 0.15) < 0.001


def test_compute_arb_edges_filters_small_spread():
    pm = _market("polymarket", "Q", 0.50)
    ks = _market("kalshi", "Q", 0.52)
    edges = compute_arb_edges([(pm, ks)])
    assert edges == []


def test_compute_arb_edges_sorted_desc():
    pairs = [
        (_market("polymarket", "Q1", 0.4), _market("kalshi", "Q1", 0.55)),
        (_market("polymarket", "Q2", 0.3), _market("kalshi", "Q2", 0.65)),
    ]
    edges = compute_arb_edges(pairs)
    assert edges[0].spread >= edges[1].spread


def test_sentiment_score_positive():
    score = _sentiment_score("trump leads surge win")
    assert score > 0.5


def test_sentiment_score_negative():
    score = _sentiment_score("market crash drop fail")
    assert score < 0.5


def test_sentiment_score_neutral():
    score = _sentiment_score("some random text with no keywords")
    assert score == 0.5


def test_compute_news_edges_creates_edge():
    pm = _market("polymarket", "Will X happen?", 0.3)
    edges = compute_news_edges([(pm, "win lead surge")])
    assert len(edges) == 1
    assert edges[0].type == "news"
    assert edges[0].source_b == "news"
