# core/shadow/promotion/rehearsal.py
from core.shadow.promotion.models import PromotionRehearsalResult
from core.shadow.confidence.models import ShadowConfidenceSnapshot
from core.strategy_reputation.retirement import (
    StrategyLifecycleState,
    StrategyRetirementDecision,
)


def rehearse_promotion(
    *,
    strategy_id: str,
    confidence_snapshot: ShadowConfidenceSnapshot,
    retirement_decision: StrategyRetirementDecision,
    min_confidence: float = 0.6,
    min_observations: int = 10,
) -> PromotionRehearsalResult:
    """
    Determines whether a strategy is eligible for promotion rehearsal.

    This function NEVER enables execution.
    """

    # Guard: retired strategies are blocked
    if retirement_decision.state != StrategyLifecycleState.ACTIVE:
        return PromotionRehearsalResult(
            strategy_id=strategy_id,
            eligible=False,
            confidence=confidence_snapshot.confidence,
            reason="strategy not active",
        )

    # Guard: insufficient confidence
    if confidence_snapshot.confidence < min_confidence:
        return PromotionRehearsalResult(
            strategy_id=strategy_id,
            eligible=False,
            confidence=confidence_snapshot.confidence,
            reason="insufficient shadow confidence",
        )

    # Guard: insufficient observations
    if confidence_snapshot.observations < min_observations:
        return PromotionRehearsalResult(
            strategy_id=strategy_id,
            eligible=False,
            confidence=confidence_snapshot.confidence,
            reason="insufficient shadow observations",
        )

    return PromotionRehearsalResult(
        strategy_id=strategy_id,
        eligible=True,
        confidence=confidence_snapshot.confidence,
        reason="eligible for promotion rehearsal",
    )
