from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class AlertEvent:
    timestamp: datetime
    severity: str   # INFO | WARN | CRITICAL
    category: str   # BROKER | RISK | DATA | EXECUTION | SYSTEM
    message: str
    context: Dict[str, Any]
