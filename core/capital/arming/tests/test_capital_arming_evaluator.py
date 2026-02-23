import pytest
from datetime import datetime, timezone

from core.capital.arming.contracts import (
    CapitalArmingState,
    CapitalArmingDecision,
)
from core.capital.arming.evaluator import CapitalArmingEvaluator


def _decision(state: CapitalArmingState):
    return CapitalArmingDecision(
        state=state,
        allowed=state != CapitalArmingState.DISARMED,
        reasons=[state.value],
        decided_at=datetime.now(tz=timezone.utc),
    )


def test_blocks_when_disarmed():
    evaluator = CapitalArmingEvaluator()

    decision = evaluator.evaluate(
        requested=CapitalArmingState.PAPER,
        current=CapitalArmingState.DISARMED,
    )

    assert decision.allowed is False
    assert decision.state == CapitalArmingState.DISARMED


def test_allows_shadow_from_disarmed():
    evaluator = CapitalArmingEvaluator()

    decision = evaluator.evaluate(
        requested=CapitalArmingState.SHADOW,
        current=CapitalArmingState.DISARMED,
    )

    assert decision.allowed is True
    assert decision.state == CapitalArmingState.SHADOW


def test_prevents_skipping_levels():
    evaluator = CapitalArmingEvaluator()

    decision = evaluator.evaluate(
        requested=CapitalArmingState.GOVERNED_LIVE,
        current=CapitalArmingState.PAPER,
    )

    assert decision.allowed is False
    assert "skip" in decision.reasons[0].lower()


def test_allows_linear_progression():
    evaluator = CapitalArmingEvaluator()

    decision = evaluator.evaluate(
        requested=CapitalArmingState.PAPER,
        current=CapitalArmingState.SHADOW,
    )

    assert decision.allowed is True
    assert decision.state == CapitalArmingState.PAPER


def test_decision_is_immutable():
    decision = _decision(CapitalArmingState.SHADOW)

    with pytest.raises(Exception):
        decision.state = CapitalArmingState.PAPER
