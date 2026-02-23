from datetime import datetime

from core.evidence.capital_scaling_audit_event import (
    CapitalScalingAuditEvent,
)


def test_capital_scaling_audit_event_contract():
    event = CapitalScalingAuditEvent(
        strategy_id="STRAT-LIVE-001",
        previous_capital=1_000_000,
        new_capital=1_200_000,
        scale_factor=1.2,
        decision_reason="SSR_STRONG_SCALE_UP",
        decision_checksum="abc123",
        timestamp=datetime.utcnow(),
    )

    assert event.strategy_id == "STRAT-LIVE-001"
    assert event.previous_capital == 1_000_000
    assert event.new_capital == 1_200_000
    assert event.scale_factor == 1.2
    assert event.decision_reason == "SSR_STRONG_SCALE_UP"
    assert event.decision_checksum == "abc123"
    assert isinstance(event.timestamp, datetime)
