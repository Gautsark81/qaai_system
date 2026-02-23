from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PaperTradeSnapshot:
    """
    Immutable snapshot of paper-trading performance.

    Governance-only evidence.
    No execution or capital authority.
    """

    paper_ssr: float
    paper_trades: int
    paper_drawdown: float
    flags: List[str]

    def validate(self) -> None:
        if not (0.0 <= self.paper_ssr <= 1.0):
            raise ValueError("paper_ssr out of bounds")
        if self.paper_trades < 0:
            raise ValueError("paper_trades must be non-negative")
        if not (0.0 <= self.paper_drawdown <= 1.0):
            raise ValueError("paper_drawdown out of bounds")
