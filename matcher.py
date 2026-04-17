# matcher.py
from __future__ import annotations
from difflib import SequenceMatcher
import config
from models import Market


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_markets(
    polymarket: list[Market], others: list[Market]
) -> list[tuple[Market, Market]]:
    """Return (polymarket_market, other_market) pairs with title similarity >= MATCH_THRESHOLD."""
    pairs = []
    for pm in polymarket:
        for other in others:
            if _similarity(pm.question, other.question) >= config.MATCH_THRESHOLD:
                pairs.append((pm, other))
    return pairs


def match_news(
    polymarket: list[Market], headlines: list[str]
) -> list[tuple[Market, str]]:
    """Return (market, headline) pairs where headline contains >= NEWS_KEYWORD_MIN market keywords."""
    pairs = []
    for pm in polymarket:
        keywords = _extract_keywords(pm.question)
        for headline in headlines:
            hits = sum(1 for kw in keywords if kw in headline)
            if hits >= config.NEWS_KEYWORD_MIN:
                pairs.append((pm, headline))
                break  # one match per market
    return pairs


def _extract_keywords(question: str) -> list[str]:
    stopwords = {
        "will", "the", "a", "an", "in", "on", "at", "to", "for",
        "of", "be", "is", "are", "by", "or", "and", "win", "wins",
        "did", "does", "do", "has", "have",
    }
    words = question.lower().split()
    return [w.strip("?.,!") for w in words
            if w.strip("?.,!") not in stopwords and len(w.strip("?.,!")) > 2]
