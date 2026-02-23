from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats


@dataclass(frozen=True)
class StrategyLearningAnnotation:
    """
    Immutable, advisory annotation describing historical lifecycle learning
    relevant to a strategy candidate.

    This object contains NO logic and does NOT influence decisions.
    """

    lifecycle_snapshot: Optional[LifecycleLearningSnapshot]
    failure_mode_stats: Optional[FailureModeStats]
    explanation: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"StrategyLearningAnnotation("
            f"lifecycle_snapshot={self.lifecycle_snapshot!r}, "
            f"failure_mode_stats={self.failure_mode_stats!r}, "
            f"explanation={self.explanation!r}"
            f")"
        )
