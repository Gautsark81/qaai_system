from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats


@dataclass(frozen=True)
class HealthLearningContext:
    """
    Immutable container for learning context attached to health outputs.

    This object is read-only and contains no behavior.
    """

    lifecycle_snapshot: Optional[LifecycleLearningSnapshot]
    failure_mode_stats: Optional[FailureModeStats]

    def __repr__(self) -> str:
        return (
            f"HealthLearningContext("
            f"lifecycle_snapshot={self.lifecycle_snapshot!r}, "
            f"failure_mode_stats={self.failure_mode_stats!r}"
            f")"
        )
