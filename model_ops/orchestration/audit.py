from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class RollbackBridgeAuditEvent:
    model_id: str
    decay_reasons: List[str]
    triggered: bool
    timestamp: datetime
