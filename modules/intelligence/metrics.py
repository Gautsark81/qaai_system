from dataclasses import dataclass
from typing import List
from .ssr import TradeResult


@dataclass(frozen=True)
class StrategyMetrics:
    total_trades: int
    winning_trades: int
    losing_trades: int
    net_pnl: float


class StrategyMetricsExtractor:
    def extract(self, trades: List[TradeResult]) -> StrategyMetrics:
        filled = [t for t in trades if t.status == "FILLED"]

        return StrategyMetrics(
            total_trades=len(filled),
            winning_trades=len([t for t in filled if t.pnl > 0]),
            losing_trades=len([t for t in filled if t.pnl < 0]),
            net_pnl=round(sum(t.pnl for t in filled), 2),
        )
