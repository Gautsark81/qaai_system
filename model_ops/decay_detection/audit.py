from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class DecayAuditEvent:
    model_id: str
    reasons: List[str]
    timestamp: datetime
