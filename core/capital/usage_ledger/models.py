from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class CapitalEventType(str, Enum):
    ALLOCATION = "allocation"
    CONSUMPTION = "consumption"
    RELEASE = "release"


@dataclass(frozen=True)
class CapitalUsageEntry:
    event_type: CapitalEventType
    strategy_id: str
    amount: float
    timestamp: datetime
    reason: str
