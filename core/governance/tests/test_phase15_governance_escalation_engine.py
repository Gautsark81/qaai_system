from core.governance.escalation.governance_escalation_engine import (
    GovernanceEscalationEngine,
)


def test_no_strikes():
    engine = GovernanceEscalationEngine()

    decision = engine.evaluate(
        governance_id="gov-1",
        strike_count=0,
    )

    assert decision.escalation_level == "NONE"
    assert decision.throttle_override is None
    assert decision.freeze_capital is False
    assert decision.zero_capital is False


def test_warning_level():
    engine = GovernanceEscalationEngine()

    decision = engine.evaluate(
        governance_id="gov-2",
        strike_count=1,
    )

    assert decision.escalation_level == "WARNING"


def test_soft_throttle():
    engine = GovernanceEscalationEngine()

    decision = engine.evaluate(
        governance_id="gov-3",
        strike_count=2,
    )

    assert decision.escalation_level == "SOFT_THROTTLE"
    assert decision.throttle_override == 0.75


def test_hard_throttle():
    engine = GovernanceEscalationEngine()

    decision = engine.evaluate(
        governance_id="gov-4",
        strike_count=3,
    )

    assert decision.escalation_level == "HARD_THROTTLE"
    assert decision.throttle_override == 0.5


def test_freeze():
    engine = GovernanceEscalationEngine()

    decision = engine.evaluate(
        governance_id="gov-5",
        strike_count=4,
    )

    assert decision.escalation_level == "FREEZE"
    assert decision.freeze_capital is True


def test_zero_capital():
    engine = GovernanceEscalationEngine()

    decision = engine.evaluate(
        governance_id="gov-6",
        strike_count=5,
    )

    assert decision.escalation_level == "ZERO_CAPITAL"
    assert decision.zero_capital is True