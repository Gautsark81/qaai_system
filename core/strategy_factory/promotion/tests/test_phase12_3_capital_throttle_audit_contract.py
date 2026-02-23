from datetime import datetime
from core.evidence.capital_throttle_audit_event import CapitalThrottleAuditEvent


def test_capital_throttle_audit_event_contract():
    event = CapitalThrottleAuditEvent(
        strategy_id="STRAT-LIVE-001",
        throttle_level=0.5,
        reason="DRAWDOWN_SPIKE",
        explanation="Intraday drawdown exceeded throttle threshold",
        decision_checksum="abc123",
        timestamp=datetime.utcnow(),
    )

    assert event.strategy_id == "STRAT-LIVE-001"
    assert event.throttle_level == 0.5
    assert event.reason == "DRAWDOWN_SPIKE"
    assert "drawdown" in event.explanation.lower()
    assert event.decision_checksum == "abc123"
