from core.operator.escalation import (
    compute_escalation,
    EscalationLevel,
)
from core.operator.trust_score import OperatorTrustScore
from core.operator.abuse_signal import OperatorAbuseSignal


def test_green_escalation_normal():
    trust = OperatorTrustScore("op1", trust=0.95, fatigue=0.1)

    decision = compute_escalation(trust, None)

    assert decision.level == EscalationLevel.GREEN
    assert decision.requires_confirmation is False
    assert decision.requires_delay is False


def test_yellow_escalation_low_trust():
    trust = OperatorTrustScore("op1", trust=0.75, fatigue=0.4)

    decision = compute_escalation(trust, None)

    assert decision.level == EscalationLevel.YELLOW
    assert decision.requires_confirmation is True
    assert decision.audit_prominence == "elevated"


def test_orange_escalation_very_low_trust():
    trust = OperatorTrustScore("op1", trust=0.55, fatigue=0.7)

    decision = compute_escalation(trust, None)

    assert decision.level == EscalationLevel.ORANGE
    assert decision.requires_delay is True


def test_red_escalation_abuse_dominates():
    trust = OperatorTrustScore("op1", trust=0.9, fatigue=0.1)
    abuse = OperatorAbuseSignal(
        operator_id="op1",
        confidence=0.8,
        reason="override abuse pattern detected",
        evidence_event_ids=[1, 2, 3],
    )

    decision = compute_escalation(trust, abuse)

    assert decision.level == EscalationLevel.RED
    assert decision.audit_prominence == "board"
    assert decision.requires_confirmation is True
