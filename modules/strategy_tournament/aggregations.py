# modules/strategy_tournament/aggregations.py

from dataclasses import dataclass
from typing import List
from modules.strategy_tournament.metrics import SymbolMetrics


@dataclass(frozen=True)
class StrategyMetrics:
    strategy_id: str
    symbols_traded: int
    total_trades: int
    total_wins: int
    total_losses: int
    overall_win_rate: float
    total_pnl: float
    max_drawdown: float


def aggregate_strategy_metrics(
    strategy_id: str,
    symbol_metrics: List[SymbolMetrics],
) -> StrategyMetrics:
    total_trades = sum(m.trades for m in symbol_metrics)
    total_wins = sum(m.wins for m in symbol_metrics)
    total_losses = sum(m.losses for m in symbol_metrics)

    overall_win_rate = (
        total_wins / total_trades if total_trades > 0 else 0.0
    )

    return StrategyMetrics(
        strategy_id=strategy_id,
        symbols_traded=len(symbol_metrics),
        total_trades=total_trades,
        total_wins=total_wins,
        total_losses=total_losses,
        overall_win_rate=overall_win_rate,
        total_pnl=sum(m.total_pnl for m in symbol_metrics),
        max_drawdown=max(m.max_drawdown for m in symbol_metrics)
        if symbol_metrics
        else 0.0,
    )
