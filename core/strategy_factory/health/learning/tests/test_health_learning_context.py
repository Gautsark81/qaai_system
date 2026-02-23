from datetime import datetime, timezone

from core.strategy_factory.health.learning.health_learning_context import (
    HealthLearningContext,
)
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats
from core.strategy_factory.health.death_reason import DeathReason


def test_health_learning_context_fields():
    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime.now(timezone.utc),
        total_strategies_observed=10,
        total_deaths=3,
        death_reason_counts={DeathReason.MAX_DRAWDOWN: 3},
        notes=None,
    )

    stats = FailureModeStats(
        total_deaths=3,
        reason_counts={DeathReason.MAX_DRAWDOWN: 3},
    )

    ctx = HealthLearningContext(
        lifecycle_snapshot=snapshot,
        failure_mode_stats=stats,
    )

    assert ctx.lifecycle_snapshot is snapshot
    assert ctx.failure_mode_stats is stats


def test_health_learning_context_is_immutable():
    ctx = HealthLearningContext(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
    )

    try:
        ctx.lifecycle_snapshot = None
        assert False, "HealthLearningContext must be immutable"
    except AttributeError:
        pass


def test_health_learning_context_repr():
    ctx = HealthLearningContext(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
    )

    text = repr(ctx)
    assert "HealthLearningContext" in text
