from core.strategy_factory.promotion.admission.live_admission_decision import (
    LiveAdmissionDecision,
)

def test_live_admission_decision_contract():
    decision = LiveAdmissionDecision(
        allowed=False,
        reason="blocked",
        explanation="test",
        next_state=None,
        evidence_checksum="abc123",
    )

    assert isinstance(decision.allowed, bool)
    assert isinstance(decision.reason, str)
    assert isinstance(decision.explanation, str)
    assert decision.next_state in (None, "LIVE")
    assert isinstance(decision.evidence_checksum, str)
