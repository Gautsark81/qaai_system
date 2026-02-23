# core/execution/paper_ledger.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Tuple


# -------------------------------------------------
# Ledger Entry (Immutable)
# -------------------------------------------------

@dataclass(frozen=True)
class PaperCapitalLedgerEntry:
    """
    Immutable record of a capital mutation caused by a paper execution.

    This represents a DELTA, not a balance.
    """

    execution_id: str
    strategy_id: str
    symbol: str

    quantity: float
    price: float

    gross_value: float
    fees: float
    slippage: float

    delta_capital: float
    recorded_at: datetime


# -------------------------------------------------
# Ledger Utilities (Pure Functions)
# -------------------------------------------------

def compute_delta_capital(
    *,
    quantity: float,
    price: float,
    fees: float,
    slippage: float,
    side: str,
) -> float:
    """
    Compute capital delta for a paper trade.

    BUY  → negative capital (cash out)
    SELL → positive capital (cash in)
    """

    gross = quantity * price
    total_cost = gross + fees + slippage

    if side == "BUY":
        return -total_cost
    elif side == "SELL":
        return total_cost
    else:
        raise ValueError(f"Unsupported side: {side}")


def total_capital(ledger: Iterable[PaperCapitalLedgerEntry]) -> float:
    """
    Derive total capital from ledger entries.
    """
    return sum(entry.delta_capital for entry in ledger)


def ledger_for_strategy(
    ledger: Iterable[PaperCapitalLedgerEntry],
    *,
    strategy_id: str,
) -> Tuple[PaperCapitalLedgerEntry, ...]:
    """
    Filter ledger entries for a single strategy.
    """
    return tuple(
        entry for entry in ledger
        if entry.strategy_id == strategy_id
    )
