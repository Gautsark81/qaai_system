from typing import Optional

from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)

from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)

from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats


class LearningRegistry:
    """
    Read-only registry for latest lifecycle learning artifacts.

    This registry:
    - Stores the most recent learning outputs
    - Does NOT mutate or interpret them
    - Acts as a safe handoff point for other components
    """

    def __init__(self) -> None:
        self._latest_snapshot: Optional[LifecycleLearningSnapshot] = None
        self._latest_failure_stats: Optional[FailureModeStats] = None

    def record_snapshot(self, snapshot: LifecycleLearningSnapshot) -> None:
        self._latest_snapshot = snapshot

    def record_failure_stats(self, stats: FailureModeStats) -> None:
        self._latest_failure_stats = stats

    def latest_snapshot(self) -> Optional[LifecycleLearningSnapshot]:
        return self._latest_snapshot

    def latest_failure_stats(self) -> Optional[FailureModeStats]:
        return self._latest_failure_stats

    def latest_annotation(self) -> Optional[StrategyLearningAnnotation]:
        return getattr(self, "_latest_annotation", None)