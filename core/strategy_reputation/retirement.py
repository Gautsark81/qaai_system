# core/strategy_reputation/retirement.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.strategy_reputation.reputation import StrategyReputation
from core.strategy_reputation.normalization import NormalizedReputation


class StrategyLifecycleState(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class StrategyRetirementDecision:
    strategy_id: str
    state: StrategyLifecycleState
    reason: str
    evidence_summary: str


# core/strategy_reputation/retirement.py (continued)

def decide_strategy_retirement(
    reputation: StrategyReputation,
    normalized: NormalizedReputation,
    *,
    min_cycles: int = 4,
    min_confidence: float = 0.6,
    negative_score_threshold: float = -10.0,
) -> StrategyRetirementDecision:
    """
    Decide whether a strategy should be retired.

    This function NEVER deletes or disables strategies.
    It only returns a governance decision.
    """

    # Default: ACTIVE
    state = StrategyLifecycleState.ACTIVE
    reason = "strategy within acceptable bounds"
    evidence = "no sustained negative signal"

    # Guard: too young to judge
    if reputation.cycles < min_cycles:
        return StrategyRetirementDecision(
            strategy_id=reputation.strategy_id,
            state=StrategyLifecycleState.ACTIVE,
            reason="insufficient career length",
            evidence_summary=f"{reputation.cycles} cycles < minimum {min_cycles}",
        )

    # Sustained negative performance
    if (
        normalized.confidence >= min_confidence
        and normalized.normalized_score <= negative_score_threshold
    ):
        state = StrategyLifecycleState.RETIRED
        reason = "sustained underperformance"
        evidence = (
            f"normalized_score={normalized.normalized_score}, "
            f"confidence={normalized.confidence}, "
            f"cycles={reputation.cycles}"
        )

    return StrategyRetirementDecision(
        strategy_id=reputation.strategy_id,
        state=state,
        reason=reason,
        evidence_summary=evidence,
    )
