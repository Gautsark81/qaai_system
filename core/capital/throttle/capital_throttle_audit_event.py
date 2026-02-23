from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CapitalThrottleAuditEvent:
    """
    Immutable audit event emitted whenever capital throttling
    is evaluated or applied.

    Phase 12.3 – Capital Throttle Audit
    Phase 12.5 – Governance chain linkage
    """

    strategy_id: str

    # Throttle expression
    throttle_level: Optional[float] = None
    throttle_factor: Optional[float] = None

    # Explanations
    reason: Optional[str] = None
    explanation: Optional[str] = None
    decision_reason: Optional[str] = None

    # Governance
    decision_checksum: Optional[str] = None
    governance_id: Optional[str] = None

    timestamp: Optional[datetime] = None

    def __post_init__(self):
        # Determinism
        if self.timestamp is None:
            raise ValueError("timestamp is required")

        # Governance chain
        if self.decision_checksum is None and self.governance_id is None:
            raise ValueError(
                "Either decision_checksum or governance_id must be provided"
            )

        # Must specify throttle expression
        if self.throttle_level is None and self.throttle_factor is None:
            raise ValueError(
                "Either throttle_level or throttle_factor must be provided"
            )

        # NO_THROTTLE case (explicitly allowed)
        if self.throttle_factor == 1.0 and self.decision_reason == "NO_THROTTLE":
            return

        # Otherwise: throttle was applied → explanation required
        if self.reason is None:
            raise ValueError("reason is required for throttle events")

        if self.explanation is None:
            raise ValueError("explanation is required for throttle events")
