from datetime import datetime, timezone

from core.evidence.capital_scaling_audit_event import CapitalScalingAuditEvent
from core.evidence.capital_throttle_audit_event import CapitalThrottleAuditEvent


def test_scaling_and_throttle_audit_share_governance_chain():
    now = datetime.now(timezone.utc)

    scaling_audit = CapitalScalingAuditEvent(
        strategy_id="STRAT-1",
        previous_capital=1_000_000,
        new_capital=1_200_000,
        scale_factor=1.2,
        decision_reason="CAPITAL_SCALE_UP",
        decision_checksum="gov-xyz",
        timestamp=now,
    )

    throttle_audit = CapitalThrottleAuditEvent(
        strategy_id="STRAT-1",
        throttle_factor=1.0,
        decision_reason="NO_THROTTLE",
        governance_id="gov-xyz",
        timestamp=now,
    )

    assert scaling_audit.decision_checksum == throttle_audit.governance_id
