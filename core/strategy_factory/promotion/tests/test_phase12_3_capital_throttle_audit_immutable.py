import pytest
from datetime import datetime
from core.evidence.capital_throttle_audit_event import CapitalThrottleAuditEvent


def test_capital_throttle_audit_event_is_immutable():
    event = CapitalThrottleAuditEvent(
        strategy_id="STRAT-LIVE-001",
        throttle_level=0.25,
        reason="VOLATILITY_SPIKE",
        explanation="Volatility exceeded throttle limit",
        decision_checksum="hash123",
        timestamp=datetime.utcnow(),
    )

    with pytest.raises(Exception):
        event.throttle_level = 1.0

    with pytest.raises(Exception):
        event.reason = "MANUAL_OVERRIDE"
