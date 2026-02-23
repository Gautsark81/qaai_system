from datetime import datetime, timezone

from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.death_reason import DeathReason


def test_lifecycle_learning_snapshot_fields():
    ts = datetime.now(timezone.utc)

    snapshot = LifecycleLearningSnapshot(
        timestamp=ts,
        total_strategies_observed=12,
        total_deaths=5,
        death_reason_counts={
            DeathReason.MAX_DRAWDOWN: 3,
            DeathReason.SSR_FAILURE: 2,
        },
        notes="early lifecycle learning",
    )

    assert snapshot.timestamp == ts
    assert snapshot.total_strategies_observed == 12
    assert snapshot.total_deaths == 5
    assert snapshot.death_reason_counts[DeathReason.MAX_DRAWDOWN] == 3
    assert snapshot.notes == "early lifecycle learning"


def test_lifecycle_learning_snapshot_is_immutable():
    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime.now(timezone.utc),
        total_strategies_observed=1,
        total_deaths=0,
        death_reason_counts={},
        notes=None,
    )

    try:
        snapshot.total_deaths = 99
        assert False, "Snapshot must be immutable"
    except AttributeError:
        pass


def test_lifecycle_learning_snapshot_repr():
    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        total_strategies_observed=10,
        total_deaths=4,
        death_reason_counts={},
        notes=None,
    )

    text = repr(snapshot)
    assert "LifecycleLearningSnapshot" in text
    assert "total_deaths=4" in text
