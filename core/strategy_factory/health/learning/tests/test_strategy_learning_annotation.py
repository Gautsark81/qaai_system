from datetime import datetime, timezone

from core.strategy_factory.health.learning.strategy_learning_annotation import (
    StrategyLearningAnnotation,
)
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats
from core.strategy_factory.health.death_reason import DeathReason



def test_strategy_learning_annotation_fields():
    snapshot = LifecycleLearningSnapshot(
        timestamp=datetime.now(timezone.utc),
        total_strategies_observed=20,
        total_deaths=6,
        death_reason_counts={DeathReason.MAX_DRAWDOWN: 6},
        notes="drawdown heavy",
    )

    stats = FailureModeStats(
        total_deaths=6,
        reason_counts={DeathReason.MAX_DRAWDOWN: 6},
    )

    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=snapshot,
        failure_mode_stats=stats,
        explanation="Most failures historically due to drawdown",
    )

    assert annotation.lifecycle_snapshot is snapshot
    assert annotation.failure_mode_stats is stats
    assert annotation.explanation.startswith("Most failures")


def test_strategy_learning_annotation_optional_fields():
    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
        explanation=None,
    )

    assert annotation.lifecycle_snapshot is None
    assert annotation.failure_mode_stats is None
    assert annotation.explanation is None


def test_strategy_learning_annotation_is_immutable():
    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
        explanation=None,
    )

    try:
        annotation.explanation = "mutate"
        assert False, "StrategyLearningAnnotation must be immutable"
    except AttributeError:
        pass


def test_strategy_learning_annotation_repr():
    annotation = StrategyLearningAnnotation(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
        explanation=None,
    )

    text = repr(annotation)
    assert "StrategyLearningAnnotation" in text
