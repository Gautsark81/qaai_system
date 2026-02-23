from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CapitalScalingAuditEvent:
    """
    Immutable audit record for live capital scaling decisions.
    """

    strategy_id: str
    previous_capital: float
    new_capital: float
    scale_factor: float
    decision_reason: str
    decision_checksum: str
    timestamp: datetime

    # Phase 12.6
    governance_chain_id: Optional[str] = None