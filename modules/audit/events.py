# modules/audit/events.py

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class AuditEvent:
    timestamp: datetime
    category: Literal[
        "STRATEGY_INTENT",
        "PLAN_CREATED",
        "PLAN_REJECTED",
        "ORDER_SUBMITTED",
        "ORDER_SKIPPED",
        "STRATEGY_DISABLED",
    ]
    entity_id: str
    message: str
