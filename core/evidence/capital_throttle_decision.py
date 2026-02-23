from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from core.evidence.capital_throttle_audit_event import (
    CapitalThrottleAuditEvent,
)


@dataclass(frozen=True)
class CapitalThrottleDecision:
    """
    Deterministic result of capital throttling evaluation.
    """

    allowed: bool
    throttle_level: float
    reason: str
    explanation: str

    decision_checksum: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)

    # Phase 12.3
    audit_event: Optional[CapitalThrottleAuditEvent] = None

    def __init__(
        self,
        *,
        allowed: bool,
        throttle_level: float,
        reason: str,
        explanation: str,
        decision_checksum: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        audit_event: Optional[CapitalThrottleAuditEvent] = None,
    ):
        object.__setattr__(self, "allowed", allowed)
        object.__setattr__(self, "throttle_level", throttle_level)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "explanation", explanation)
        object.__setattr__(self, "decision_checksum", decision_checksum)
        object.__setattr__(
            self,
            "timestamp",
            timestamp or datetime.now(timezone.utc),
        )
        object.__setattr__(self, "audit_event", audit_event)
