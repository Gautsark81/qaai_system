from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.v2.paper_trading.contracts import PaperFill


@dataclass(frozen=True)
class PnLEntry:
    strategy_id: str
    symbol: str
    delta: float


class PnLLedger:
    """
    Records paper PnL entries deterministically.
    """

    def __init__(self):
        self._entries: List[PnLEntry] = []

    def record(self, *, fill: PaperFill, strategy_id: str) -> None:
        if fill.side == "BUY":
            delta = -fill.price * fill.quantity
        elif fill.side == "SELL":
            delta = fill.price * fill.quantity
        else:
            raise ValueError(f"Unknown side: {fill.side}")

        self._entries.append(
            PnLEntry(
                strategy_id=strategy_id,
                symbol=fill.symbol,
                delta=delta,
            )
        )

    def entries(self) -> List[PnLEntry]:
        return list(self._entries)
