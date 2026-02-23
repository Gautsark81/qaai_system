from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from core.strategy_factory.health.death_reason import DeathReason


@dataclass(frozen=True)
class LifecycleLearningSnapshot:
    """
    Immutable snapshot of lifecycle learning signals.

    This represents aggregated, explainable facts about
    observed strategy lifecycles at a point in time.
    """

    timestamp: datetime
    total_strategies_observed: int
    total_deaths: int
    death_reason_counts: Dict[DeathReason, int]
    notes: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"LifecycleLearningSnapshot("
            f"timestamp={self.timestamp.isoformat()}, "
            f"total_strategies_observed={self.total_strategies_observed}, "
            f"total_deaths={self.total_deaths}, "
            f"death_reason_counts={dict(self.death_reason_counts)}, "
            f"notes={self.notes!r}"
            f")"
        )
