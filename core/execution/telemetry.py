from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ExecutionEvent:
    """
    Atomic execution event.
    Immutable and replay-safe.
    """
    timestamp: datetime
    event_type: str
    message: str


@dataclass(frozen=True)
class ExecutionTelemetry:
    """
    Read-only execution telemetry snapshot.
    """
    execution_id: str
    started_at: datetime
    completed_at: datetime | None

    total_orders: int
    filled_orders: int
    rejected_orders: int
    cancelled_orders: int

    events: Tuple[ExecutionEvent, ...]
