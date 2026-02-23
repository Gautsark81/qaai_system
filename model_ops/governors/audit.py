from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class RollbackAuditEvent:
    model_id: str
    old_weight: float
    new_weight: float
    reasons: List[str]
    timestamp: datetime
