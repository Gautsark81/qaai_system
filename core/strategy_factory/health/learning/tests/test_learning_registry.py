from datetime import datetime, timezone

from core.strategy_factory.health.learning.learning_registry import LearningRegistry
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats
from core.strategy_factory.health.death_reason import DeathReason


def test_learning_registry_starts_empty():
    registry = LearningRegistry()

    assert registry.latest_snapshot() is None
    assert registry.latest_failure_stats() is None


def test_learning_registry_records_and_returns_latest():
    registry = LearningRegistry()

    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime.now(timezone.utc),
        total_strategies_observed=10,
        total_deaths=4,
        death_reason_counts={DeathReason.MAX_DRAWDOWN: 4},
        notes=None,
    )

    stats = FailureModeStats(
        total_deaths=4,
        reason_counts={DeathReason.MAX_DRAWDOWN: 4},
    )

    registry.record_snapshot(snapshot)
    registry.record_failure_stats(stats)

    assert registry.latest_snapshot() is snapshot
    assert registry.latest_failure_stats() is stats


def test_learning_registry_is_read_only():
    registry = LearningRegistry()

    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime.now(timezone.utc),
        total_strategies_observed=1,
        total_deaths=0,
        death_reason_counts={},
        notes=None,
    )

    registry.record_snapshot(snapshot)

    retrieved = registry.latest_snapshot()

    try:
        retrieved.total_deaths = 99
        assert False, "Registry must not allow mutation"
    except AttributeError:
        pass
