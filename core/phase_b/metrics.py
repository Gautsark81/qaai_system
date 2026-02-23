from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrategyMetrics:
    """
    Rolling, read-only performance metrics.
    """
    dna: str
    trades: int
    wins: int
    losses: int
    pnl: float

    @property
    def win_rate(self) -> Optional[float]:
        if self.trades == 0:
            return None
        return self.wins / self.trades
