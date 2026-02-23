from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CapitalGovernanceDecision:
    """
    Immutable governance decision.
    """
    strategy_dna: str
    decision: str              # APPROVE | BLOCK | ESCALATE
    reason: str
    approved_by: Optional[str]
    timestamp: datetime
