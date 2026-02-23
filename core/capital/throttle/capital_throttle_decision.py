from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from core.capital.throttle.capital_throttle_audit_event import CapitalThrottleAuditEvent


@dataclass(frozen=True)
class CapitalThrottleDecision:
    """
    Deterministic result of capital throttling evaluation.

    Phase 12.3 — Throttle decision
    Phase 12.5 — Governance cross-linking
    """

    allowed: bool

    # Canonical internal value
    throttle_level: float

    reason: str
    explanation: str

    # Phase 12.5 — governance chain
    governance_id: Optional[str] = None

    decision_checksum: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)

    audit_event: Optional[CapitalThrottleAuditEvent] = None

    def __init__(
        self,
        *,
        allowed: bool,
        throttle_level: Optional[float] = None,
        throttle_factor: Optional[float] = None,
        reason: str,
        explanation: str,
        governance_id: Optional[str] = None,
        decision_checksum: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        audit_event: Optional[CapitalThrottleAuditEvent] = None,
    ):
        if throttle_level is None and throttle_factor is None:
            raise ValueError(
                "Either throttle_level or throttle_factor must be provided"
            )

        resolved_throttle = (
            throttle_level
            if throttle_level is not None
            else throttle_factor
        )

        object.__setattr__(self, "allowed", allowed)
        object.__setattr__(self, "throttle_level", resolved_throttle)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "explanation", explanation)
        object.__setattr__(self, "governance_id", governance_id)
        object.__setattr__(self, "decision_checksum", decision_checksum)
        object.__setattr__(
            self,
            "timestamp",
            timestamp or datetime.now(timezone.utc),
        )
        object.__setattr__(self, "audit_event", audit_event)

    # Backward + test compatibility
    @property
    def throttle_factor(self) -> float:
        return self.throttle_level
