# core/strategy_reputation/reputation.py
from dataclasses import dataclass
from typing import List
from core.strategy_reputation.performance_cycle import PerformanceCycle


@dataclass(frozen=True)
class StrategyReputation:
    strategy_id: str
    cycles: int
    total_pnl: float
    avg_sharpe: float
    worst_drawdown: float


def compute_strategy_reputation(
    strategy_id: str,
    cycles: List[PerformanceCycle],
) -> StrategyReputation:
    relevant = [c for c in cycles if c.strategy_id == strategy_id]

    if not relevant:
        return StrategyReputation(
            strategy_id=strategy_id,
            cycles=0,
            total_pnl=0.0,
            avg_sharpe=0.0,
            worst_drawdown=0.0,
        )

    total_pnl = sum(c.pnl for c in relevant)
    avg_sharpe = sum(c.sharpe for c in relevant) / len(relevant)
    worst_drawdown = max(c.max_drawdown for c in relevant)

    return StrategyReputation(
        strategy_id=strategy_id,
        cycles=len(relevant),
        total_pnl=round(total_pnl, 2),
        avg_sharpe=round(avg_sharpe, 3),
        worst_drawdown=round(worst_drawdown, 3),
    )
