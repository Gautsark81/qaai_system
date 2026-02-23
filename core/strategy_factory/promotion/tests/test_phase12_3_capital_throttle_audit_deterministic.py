from core.evidence.capital_throttle_audit_event import CapitalThrottleAuditEvent
from datetime import datetime


def test_capital_throttle_audit_is_deterministic():
    ts = datetime.utcnow()

    e1 = CapitalThrottleAuditEvent(
        strategy_id="STRAT-1",
        throttle_level=0.5,
        reason="SSR_DECAY",
        explanation="SSR dropped below threshold",
        decision_checksum="abc",
        timestamp=ts,
    )

    e2 = CapitalThrottleAuditEvent(
        strategy_id="STRAT-1",
        throttle_level=0.5,
        reason="SSR_DECAY",
        explanation="SSR dropped below threshold",
        decision_checksum="abc",
        timestamp=ts,
    )

    assert e1 == e2
