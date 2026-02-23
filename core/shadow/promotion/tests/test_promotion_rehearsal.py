from core.shadow.promotion.rehearsal import rehearse_promotion
from core.shadow.confidence.models import ShadowConfidenceSnapshot
from core.strategy_reputation.retirement import (
    StrategyRetirementDecision,
    StrategyLifecycleState,
)


def test_retired_strategy_not_eligible():
    snap = ShadowConfidenceSnapshot("s1", confidence=0.9, observations=20, last_divergence_score=0.1)
    retirement = StrategyRetirementDecision(
        strategy_id="s1",
        state=StrategyLifecycleState.RETIRED,
        reason="retired",
        evidence_summary="",
    )

    result = rehearse_promotion(
        strategy_id="s1",
        confidence_snapshot=snap,
        retirement_decision=retirement,
    )

    assert not result.eligible


def test_low_confidence_not_eligible():
    snap = ShadowConfidenceSnapshot("s1", confidence=0.3, observations=30, last_divergence_score=0.1)
    retirement = StrategyRetirementDecision(
        strategy_id="s1",
        state=StrategyLifecycleState.ACTIVE,
        reason="ok",
        evidence_summary="",
    )

    result = rehearse_promotion(
        strategy_id="s1",
        confidence_snapshot=snap,
        retirement_decision=retirement,
    )

    assert not result.eligible


def test_insufficient_observations_not_eligible():
    snap = ShadowConfidenceSnapshot("s1", confidence=0.8, observations=5, last_divergence_score=0.1)
    retirement = StrategyRetirementDecision(
        strategy_id="s1",
        state=StrategyLifecycleState.ACTIVE,
        reason="ok",
        evidence_summary="",
    )

    result = rehearse_promotion(
        strategy_id="s1",
        confidence_snapshot=snap,
        retirement_decision=retirement,
    )

    assert not result.eligible


def test_eligible_strategy_passes():
    snap = ShadowConfidenceSnapshot("s1", confidence=0.85, observations=25, last_divergence_score=0.05)
    retirement = StrategyRetirementDecision(
        strategy_id="s1",
        state=StrategyLifecycleState.ACTIVE,
        reason="ok",
        evidence_summary="",
    )

    result = rehearse_promotion(
        strategy_id="s1",
        confidence_snapshot=snap,
        retirement_decision=retirement,
    )

    assert result.eligible
    assert "eligible" in result.reason
