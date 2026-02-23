from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class GovernanceEvent:
    event_id: UUID
    strategy_id: str
    snapshot_id: UUID
    decision: str
    reason: str
    approved_by: str
    capital_limit: float | None
    created_at: datetime
