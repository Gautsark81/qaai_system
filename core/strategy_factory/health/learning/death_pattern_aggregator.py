from collections import Counter
from datetime import datetime
from typing import Iterable, Dict

from core.strategy_factory.health.death_attribution import DeathAttribution
from core.strategy_factory.health.death_reason import DeathReason
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)


class DeathPatternAggregator:
    """
    Aggregates death events into explainable lifecycle learning facts.

    This class is:
    - Stateless
    - Deterministic
    - Side-effect free
    """

    def aggregate(
        self,
        *,
        events: Iterable[DeathAttribution],
        total_strategies_observed: int,
        timestamp: datetime,
    ) -> LifecycleLearningSnapshot:
        reason_counts: Dict[DeathReason, int] = Counter(
            event.reason for event in events
        )

        total_deaths = sum(reason_counts.values())

        return LifecycleLearningSnapshot(
            timestamp=timestamp,
            total_strategies_observed=total_strategies_observed,
            total_deaths=total_deaths,
            death_reason_counts=dict(reason_counts),
            notes=None,
        )
