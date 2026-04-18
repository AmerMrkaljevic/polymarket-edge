# Polymarket Edge Finder

> Detect mispriced prediction markets and trade the edge — paper or live.

Polls Polymarket, Kalshi, Manifold, and Metaculus every 60 seconds. Fuzzy-matches markets across sources to find arbitrage spreads. Also scans RSS news headlines for sentiment divergence. Displays a live `rich` dashboard in the terminal. Places trades via paper simulation or real Polymarket CLOB orders.

## Requirements

- Python 3.11+
- Tor is NOT required — all APIs are clearnet

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Paper trading mode (default — no real money)
python3 main.py

# Live trading: set PAPER_TRADING = False in config.py, then set credentials
cp .env.example .env
# fill in your Polymarket wallet private key and API credentials
python3 main.py
```

## Configuration (config.py)

| Variable | Default | Description |
|---|---|---|
| `POLL_INTERVAL` | 60 | Seconds between polls |
| `MIN_EDGE_SIZE` | 0.05 | Minimum spread to show/trade |
| `MAX_POSITION_PCT` | 0.05 | Max 5% of bankroll per position |
| `MAX_TOTAL_EXPOSURE_PCT` | 0.25 | Max 25% total open exposure |
| `PAPER_TRADING` | True | Set False for live mode |
| `BANKROLL` | 1000.0 | USDC balance for sizing |
| `MATCH_THRESHOLD` | 0.65 | Fuzzy match similarity cutoff |
| `NEWS_KEYWORD_MIN` | 3 | Min keyword hits for news edge |

## Polymarket API credentials (live mode only)

1. Create a Polymarket account and fund it with USDC on Polygon
2. Generate API credentials from your account settings
3. Fill in `.env` with your private key and API credentials

## Architecture

```
main.py       Poll loop — fetches, matches, analyzes, trades, renders
sources/      One module per data source (polymarket, kalshi, manifold, metaculus, news)
matcher.py    Fuzzy title matching + news keyword matching
analyzer.py   Arb spread + news sentiment edge computation
trader.py     Risk checks, position sizing, order placement
broker.py     PaperBroker | LiveBroker (same interface)
positions.py  SQLite position tracking
dashboard.py  Rich terminal table
config.py     All constants
```

## Disclaimer

This tool is for research and educational use. Prediction market trading carries financial risk. Never risk money you cannot afford to lose.
