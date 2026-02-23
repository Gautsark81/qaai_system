from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from .models import GovernanceSnapshot, GovernanceDriftSignal


@dataclass(frozen=True)
class GovernanceDriftSnapshot:
    """
    Deterministic snapshot of detected governance drift.
    """
    baseline: GovernanceSnapshot
    current: GovernanceSnapshot
    drift_signals: Tuple[GovernanceDriftSignal, ...]
    generated_at: datetime
