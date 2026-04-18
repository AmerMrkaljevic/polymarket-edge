# dashboard.py
from __future__ import annotations
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich import box
import config
from models import Edge, Position

console = Console()


def render(edges: list[Edge], positions: list[Position], next_poll_in: int) -> None:
    """Clear terminal and render edges + positions tables."""
    mode_label = "⚠ LIVE" if not config.PAPER_TRADING else "PAPER"
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")

    edges_table = Table(
        title=f"EDGES  (updated {now}, next in {next_poll_in}s)",
        box=box.SIMPLE_HEAVY,
    )
    edges_table.add_column("Type", style="cyan", width=6)
    edges_table.add_column("Question", width=44)
    edges_table.add_column("Poly", justify="right", width=6)
    edges_table.add_column("Source", width=12)
    edges_table.add_column("Other", justify="right", width=6)
    edges_table.add_column("Spread", justify="right", width=10)

    for e in edges[:15]:
        spread_str = f"{e.spread:.2f}"
        if e.spread >= 0.10:
            spread_str += " 🔥"
        edges_table.add_row(
            e.type.upper(),
            e.question[:44],
            f"{e.price_a:.2f}",
            e.source_b,
            f"{e.price_b:.2f}" if e.type == "arb" else "sent.",
            spread_str,
        )

    pos_table = Table(
        title=f"POSITIONS  [{mode_label}]",
        box=box.SIMPLE_HEAVY,
    )
    pos_table.add_column("Question", width=44)
    pos_table.add_column("Side", width=5)
    pos_table.add_column("Entry", justify="right", width=6)
    pos_table.add_column("Current", justify="right", width=8)
    pos_table.add_column("PnL", justify="right", width=12)

    for p in positions:
        pnl_color = "green" if p.pnl >= 0 else "red"
        sign = "+" if p.pnl >= 0 else "-"
        pnl_str = f"[{pnl_color}]{sign}${abs(p.pnl):.2f}[/{pnl_color}]"
        pos_table.add_row(
            p.question[:44],
            p.side,
            f"{p.entry_price:.2f}",
            f"{p.current_price:.2f}",
            pnl_str,
        )

    console.clear()
    console.print(edges_table)
    console.print(pos_table)
