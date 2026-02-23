from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass(frozen=True)
class ExecutionAuditEvent:
    model_id: str
    mode: str
    payload: Dict[str, Any]
    timestamp: datetime
