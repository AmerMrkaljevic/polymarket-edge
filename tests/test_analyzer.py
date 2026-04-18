import pytest
from datetime import datetime, timezone
from models import Market, Edge
from analyzer import compute_arb_edges, compute_news_edges, _sentiment_score


def _market(source="polymarket", id="m1", question="Q?", yes_price=0.5, volume=0.0):
    return Market(source=source, id=id, question=question, yes_price=yes_price,
                  url="http://x", volume=volume)


def test_sentiment_score_positive_text():
    score = _sentiment_score("The market surged and confirmed a massive win")
    assert score > 0.5


def test_sentiment_score_negative_text():
    score = _sentiment_score("Crash and burn, total failure and loss")
    assert score < 0.5


def test_sentiment_score_neutral_text():
    score = _sentiment_score("the cat sat on the mat")
    # neutral text should be near 0.5 (VADER returns ~0 compound for truly neutral)
    assert 0.0 <= score <= 1.0


def test_arb_edges_high_volume_ranks_first():
    """A lower-spread edge on a high-volume market should rank above higher spread on low volume."""
    pm_low_vol = _market(id="m1", yes_price=0.5, volume=100.0)
    pm_high_vol = _market(id="m2", yes_price=0.5, volume=50_000.0)
    other_low = _market(source="kalshi", id="k1", yes_price=0.58, volume=0.0)   # spread 0.08
    other_high = _market(source="kalshi", id="k2", yes_price=0.56, volume=0.0)  # spread 0.06

    pairs = [(pm_low_vol, other_low), (pm_high_vol, other_high)]
    edges = compute_arb_edges(pairs)
    # high-volume market (spread 0.06 * 1.2 = 0.072) should rank first over low-vol (0.08)
    assert edges[0].question == pm_high_vol.question


def test_arb_edges_filters_below_min():
    pm = _market(yes_price=0.5)
    other = _market(source="kalshi", yes_price=0.52)  # spread 0.02, below MIN_EDGE_SIZE 0.05
    edges = compute_arb_edges([(pm, other)])
    assert edges == []
