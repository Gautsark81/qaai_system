# modules/strategy_tournament/metrics.py

from dataclasses import dataclass
from typing import List
from modules.strategy_tournament.result_schema import StrategyRunResult


@dataclass(frozen=True)
class SymbolMetrics:
    symbol: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    max_drawdown: float


def compute_symbol_metrics(run: StrategyRunResult) -> SymbolMetrics:
    trades = run.trades
    wins = sum(1 for t in trades if t.pnl > 0)
    losses = sum(1 for t in trades if t.pnl <= 0)

    trade_count = len(trades)
    win_rate = wins / trade_count if trade_count > 0 else 0.0

    return SymbolMetrics(
        symbol=run.symbol,
        trades=trade_count,
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        total_pnl=run.total_pnl,
        max_drawdown=run.max_drawdown,
    )
