from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CapitalAuditEvent:
    model_id: str
    old_weight: float
    new_weight: float
    ladder_step: str
    timestamp: datetime
