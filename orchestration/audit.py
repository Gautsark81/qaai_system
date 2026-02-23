from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class DryRunAuditEvent:
    model_id: str
    action: str
    payload: Dict[str, Any]
    timestamp: datetime
