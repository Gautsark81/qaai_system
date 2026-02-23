from dataclasses import dataclass
from typing import Dict, Literal
from datetime import datetime, timezone


CapitalEventType = Literal[
    "ALLOCATED",
    "RELEASED",
    "REBALANCED",
]


@dataclass(frozen=True)
class CapitalEvent:
    event_type: CapitalEventType
    allocations: Dict[str, float]
    total_allocated: float
    ts_utc: datetime

    @staticmethod
    def now(
        event_type: CapitalEventType,
        allocations: Dict[str, float],
        total_allocated: float,
    ) -> "CapitalEvent":
        return CapitalEvent(
            event_type=event_type,
            allocations=dict(allocations),
            total_allocated=total_allocated,
            ts_utc=datetime.now(tz=timezone.utc),
        )
