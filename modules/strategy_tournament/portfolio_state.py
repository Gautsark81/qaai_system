# modules/strategy_tournament/portfolio_state.py

from dataclasses import dataclass
from typing import Dict, List
from modules.strategy_tournament.metrics import SymbolMetrics


@dataclass(frozen=True)
class PortfolioState:
    """
    Represents aggregate portfolio behavior
    WITHOUT a candidate strategy.
    """
    symbol_metrics: Dict[str, List[SymbolMetrics]]

    @property
    def symbols(self) -> int:
        return len(self.symbol_metrics)

    @property
    def total_pnl(self) -> float:
        return sum(
            m.total_pnl
            for metrics in self.symbol_metrics.values()
            for m in metrics
        )

    @property
    def max_drawdown(self) -> float:
        return max(
            (m.max_drawdown for metrics in self.symbol_metrics.values() for m in metrics),
            default=0.0,
        )
