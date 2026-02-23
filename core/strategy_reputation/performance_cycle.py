# core/strategy_reputation/performance_cycle.py
from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceCycle:
    strategy_id: str
    cycle_id: str
    pnl: float
    max_drawdown: float
    sharpe: float
    trades: int
