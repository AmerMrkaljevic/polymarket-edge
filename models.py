from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Market:
    source: str
    id: str
    question: str
    yes_price: float  # 0.0–1.0
    url: str


@dataclass
class Edge:
    type: str         # "arb" | "news"
    question: str
    source_a: str
    price_a: float
    source_b: str
    price_b: float
    spread: float
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Position:
    market_id: str
    question: str
    side: str         # "YES" | "NO"
    entry_price: float
    size: float
    current_price: float = 0.0
    pnl: float = 0.0
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "open"
    id: int | None = None
