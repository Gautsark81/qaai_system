from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from core.evidence.capital_scaling_audit_event import CapitalScalingAuditEvent


@dataclass(frozen=True)
class CapitalScalingDecision:
    """
    Deterministic outcome of a live capital scaling evaluation.
    """

    allowed: bool
    scale_factor: float
    reason: str
    explanation: str

    evidence_checksum: Optional[str] = None
    timestamp: datetime = datetime.now(timezone.utc)
    audit_event: Optional[CapitalScalingAuditEvent] = None

    # Phase 12.6
    governance_chain_id: Optional[str] = None

    def __init__(
        self,
        *,
        allowed: bool,
        scale_factor: float,
        reason: str,
        explanation: str,
        evidence_checksum: Optional[str] = None,
        decision_checksum: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        audit_event: Optional[CapitalScalingAuditEvent] = None,
        governance_chain_id: Optional[str] = None,
    ):
        object.__setattr__(self, "allowed", allowed)
        object.__setattr__(self, "scale_factor", scale_factor)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "explanation", explanation)

        checksum = decision_checksum or evidence_checksum
        object.__setattr__(self, "evidence_checksum", checksum)

        object.__setattr__(
            self,
            "timestamp",
            timestamp or datetime.now(timezone.utc),
        )

        object.__setattr__(self, "audit_event", audit_event)
        object.__setattr__(self, "governance_chain_id", governance_chain_id)

    @property
    def decision_checksum(self) -> Optional[str]:
        return self.evidence_checksum