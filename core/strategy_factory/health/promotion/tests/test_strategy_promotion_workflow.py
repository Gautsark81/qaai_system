from datetime import datetime, timezone

import pytest

from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)
from core.strategy_factory.health.promotion.strategy_promotion_workflow import (
    PromotionDecision,
    PromotionDecisionStatus,
    StrategyPromotionWorkflow,
)


def utc_now():
    return datetime.now(timezone.utc)


def test_new_promotion_decision_starts_pending():
    workflow = StrategyPromotionWorkflow()

    decision = workflow.propose_promotion(
        strategy_id="s1",
        proposed_action=StrategyLifecycleAction.PROMOTE,
        proposed_at=utc_now(),
    )

    assert decision.decision_status == PromotionDecisionStatus.PENDING
    assert decision.advisory_only is True


def test_only_one_pending_decision_per_strategy():
    workflow = StrategyPromotionWorkflow()

    workflow.propose_promotion(
        strategy_id="s1",
        proposed_action=StrategyLifecycleAction.PROMOTE,
        proposed_at=utc_now(),
    )

    with pytest.raises(ValueError):
        workflow.propose_promotion(
            strategy_id="s1",
            proposed_action=StrategyLifecycleAction.PROMOTE,
            proposed_at=utc_now(),
        )


def test_approve_promotion():
    workflow = StrategyPromotionWorkflow()

    decision = workflow.propose_promotion(
        strategy_id="s1",
        proposed_action=StrategyLifecycleAction.PROMOTE,
        proposed_at=utc_now(),
    )

    approved = workflow.decide(
        decision_id=decision.decision_id,
        status=PromotionDecisionStatus.APPROVED,
        decided_by="operator_1",
        reason="Looks good",
        decided_at=utc_now(),
    )

    assert approved.decision_status == PromotionDecisionStatus.APPROVED
    assert approved.decided_by == "operator_1"


def test_reject_promotion():
    workflow = StrategyPromotionWorkflow()

    decision = workflow.propose_promotion(
        strategy_id="s1",
        proposed_action=StrategyLifecycleAction.PROMOTE,
        proposed_at=utc_now(),
    )

    rejected = workflow.decide(
        decision_id=decision.decision_id,
        status=PromotionDecisionStatus.REJECTED,
        decided_by="risk_team",
        reason="Insufficient sample size",
        decided_at=utc_now(),
    )

    assert rejected.decision_status == PromotionDecisionStatus.REJECTED


def test_cannot_decide_twice():
    workflow = StrategyPromotionWorkflow()

    decision = workflow.propose_promotion(
        strategy_id="s1",
        proposed_action=StrategyLifecycleAction.PROMOTE,
        proposed_at=utc_now(),
    )

    workflow.decide(
        decision_id=decision.decision_id,
        status=PromotionDecisionStatus.DEFERRED,
        decided_by="operator",
        reason="Wait for more data",
        decided_at=utc_now(),
    )

    with pytest.raises(ValueError):
        workflow.decide(
            decision_id=decision.decision_id,
            status=PromotionDecisionStatus.APPROVED,
            decided_by="operator",
            reason="Changed mind",
            decided_at=utc_now(),
        )
