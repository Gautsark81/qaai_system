from core.capital.throttle.capital_throttle_decision import CapitalThrottleDecision
from core.evidence.capital_throttle_audit_event import CapitalThrottleAuditEvent
from datetime import datetime


def test_throttle_decision_links_audit_event():
    audit = CapitalThrottleAuditEvent(
        strategy_id="STRAT-2",
        throttle_level=0.3,
        reason="RISK_SPIKE",
        explanation="Risk spike detected",
        decision_checksum="chk1",
        timestamp=datetime.utcnow(),
    )

    decision = CapitalThrottleDecision(
        allowed=False,
        throttle_level=0.3,
        reason="RISK_SPIKE",
        explanation="Throttle applied due to risk",
        decision_checksum="chk1",
        audit_event=audit,
    )

    assert decision.audit_event is audit
