# core/strategy_factory/capital/escalation/audit_record.py

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EscalationAuditRecord:
    """
    Immutable audit artifact representing an escalation decision.

    This record is:
    - Deterministic
    - Replayable
    - Governance-bound
    - Immutable (frozen dataclass)
    """

    strategy_id: str
    symbol: str
    timestamp: datetime
    escalation_level: str
    reason: str
    approved: bool
    capital_before: float
    capital_after: float
    governance_chain_id: str

    def to_dict(self) -> dict:
        return {
            "strategy_id": self.strategy_id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "escalation_level": self.escalation_level,
            "reason": self.reason,
            "approved": self.approved,
            "capital_before": self.capital_before,
            "capital_after": self.capital_after,
            "governance_chain_id": self.governance_chain_id,
        }