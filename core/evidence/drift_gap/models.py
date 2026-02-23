from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Dict, Any


class DriftGapType(str, Enum):
    POSITION = "position"
    CAPITAL = "capital"
    ORDER_STATE = "order_state"


class DriftSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DriftGapRecord:
    gap_type: DriftGapType
    severity: DriftSeverity
    detected_at: datetime
    details: Dict[str, Any]
