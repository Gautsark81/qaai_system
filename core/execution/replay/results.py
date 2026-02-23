from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ReplayEvent:
    """
    Event reconstructed during replay.
    """
    timestamp: datetime
    event_type: str
    message: str


@dataclass(frozen=True)
class ReplayResult:
    """
    Outcome of a replay run.
    """
    replay_id: str
    execution_id: str
    completed_at: datetime

    reconstructed_events: Tuple[ReplayEvent, ...]
    invariant_violations: Tuple[str, ...]
