from datetime import datetime
from core.evidence.capital_throttle_audit_event import CapitalThrottleAuditEvent


def test_throttle_audit_is_append_only():
    event = CapitalThrottleAuditEvent(
        strategy_id="STRAT-LEDGER",
        throttle_level=0.4,
        reason="DRAWDOWN_ACCELERATION",
        explanation="Rapid drawdown acceleration",
        decision_checksum="ledger123",
        timestamp=datetime.utcnow(),
    )

    # Assert no mutating methods exist
    forbidden = ["update", "modify", "replace", "rollback"]
    for name in forbidden:
        assert not hasattr(event, name)
