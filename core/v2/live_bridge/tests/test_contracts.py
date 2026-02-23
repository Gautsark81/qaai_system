from datetime import datetime, timedelta

from core.v2.live_bridge.contracts import (
    LiveApprovalRecord,
    LiveGateDecision,
)


def test_live_approval_record_is_immutable():
    r = LiveApprovalRecord(
        strategy_id="s1",
        approved_by="operator",
        approved_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1),
        notes="Approved for limited live trial",
    )

    try:
        r.strategy_id = "s2"
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_live_gate_decision_structure():
    d = LiveGateDecision(
        strategy_id="s1",
        allowed=False,
        reasons=["no_approval"],
        evaluated_at=datetime.utcnow(),
    )

    assert d.allowed is False
    assert "no_approval" in d.reasons
