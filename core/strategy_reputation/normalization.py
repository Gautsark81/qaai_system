# core/strategy_reputation/normalization.py
from dataclasses import dataclass
from typing import List
import math
from statistics import pstdev
from core.strategy_reputation.performance_cycle import PerformanceCycle


@dataclass(frozen=True)
class NormalizedReputation:
    strategy_id: str
    confidence: float           # 0.0 → 1.0
    stability_penalty: float    # 0.0 → 1.0
    normalized_score: float    # can be negative

# core/strategy_reputation/normalization.py (continued)

def normalize_strategy_reputation(
    strategy_id: str,
    cycles: List[PerformanceCycle],
) -> NormalizedReputation:
    """
    Applies anti-luck normalization to strategy performance.
    """

    relevant = [c for c in cycles if c.strategy_id == strategy_id]

    if not relevant:
        return NormalizedReputation(
            strategy_id=strategy_id,
            confidence=0.0,
            stability_penalty=0.0,
            normalized_score=0.0,
        )

    n = len(relevant)

    # Confidence grows logarithmically with cycles
    confidence = min(1.0, math.log(n + 1) / math.log(10))

    # Sharpe stability (lower variance = better)
    sharpes = [c.sharpe for c in relevant]
    sharpe_std = pstdev(sharpes) if len(sharpes) > 1 else 0.0
    sharpe_penalty = min(1.0, sharpe_std)

    # Drawdown instability penalty
    drawdowns = [c.max_drawdown for c in relevant]
    dd_std = pstdev(drawdowns) if len(drawdowns) > 1 else 0.0
    drawdown_penalty = min(1.0, dd_std * 2)

    stability_penalty = min(1.0, sharpe_penalty + drawdown_penalty)

    avg_pnl = sum(c.pnl for c in relevant) / n

    normalized_score = round(
        avg_pnl * confidence * (1.0 - stability_penalty),
        3,
    )

    return NormalizedReputation(
        strategy_id=strategy_id,
        confidence=round(confidence, 3),
        stability_penalty=round(stability_penalty, 3),
        normalized_score=normalized_score,
    )
