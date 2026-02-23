from datetime import datetime, timezone

from core.strategy_factory.health.learning.read_hooks import (
    get_latest_learning_snapshot,
    get_latest_failure_mode_stats,
)
from core.strategy_factory.health.learning.learning_registry import LearningRegistry
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats
from core.strategy_factory.health.death_reason import DeathReason


def test_read_hooks_return_none_when_empty():
    registry = LearningRegistry()

    assert get_latest_learning_snapshot(registry) is None
    assert get_latest_failure_mode_stats(registry) is None


def test_read_hooks_return_latest_objects():
    registry = LearningRegistry()

    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime.now(timezone.utc),
        total_strategies_observed=5,
        total_deaths=2,
        death_reason_counts={DeathReason.MAX_DRAWDOWN: 2},
        notes=None,
    )

    stats = FailureModeStats(
        total_deaths=2,
        reason_counts={DeathReason.MAX_DRAWDOWN: 2},
    )

    registry.record_snapshot(snapshot)
    registry.record_failure_stats(stats)

    assert get_latest_learning_snapshot(registry) is snapshot
    assert get_latest_failure_mode_stats(registry) is stats
