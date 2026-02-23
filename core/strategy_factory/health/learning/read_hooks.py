from typing import Optional

from core.strategy_factory.health.learning.learning_registry import LearningRegistry
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats


def get_latest_learning_snapshot(
    registry: LearningRegistry,
) -> Optional[LifecycleLearningSnapshot]:
    """
    Read-only access to the latest lifecycle learning snapshot.
    """
    return registry.latest_snapshot()


def get_latest_failure_mode_stats(
    registry: LearningRegistry,
) -> Optional[FailureModeStats]:
    """
    Read-only access to the latest failure mode statistics.
    """
    return registry.latest_failure_stats()
