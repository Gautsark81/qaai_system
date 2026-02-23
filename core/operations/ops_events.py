from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional


OpsEventType = Literal[
    "daily_check",
    "weekly_check",
    "kill_switch_drill",
    "governance_dry_run",
]


@dataclass(frozen=True)
class OpsEvent:
    event_type: OpsEventType
    operator: str
    notes: str
    occurred_at: datetime

    @staticmethod
    def now(
        *,
        event_type: OpsEventType,
        operator: str,
        notes: str,
    ) -> "OpsEvent":
        return OpsEvent(
            event_type=event_type,
            operator=operator,
            notes=notes,
            occurred_at=datetime.now(timezone.utc),
        )
