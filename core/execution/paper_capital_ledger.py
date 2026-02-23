from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaperCapitalLedgerEntry:
    """
    Virtual capital ledger entry for Paper Trading.

    Properties:
    - Virtual only
    - Deterministic
    - No pricing
    - No PnL
    """

    strategy_id: str
    delta_capital: float
    is_virtual: bool = True
