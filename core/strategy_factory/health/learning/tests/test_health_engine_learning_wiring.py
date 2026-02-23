from datetime import datetime, timezone

from core.strategy_factory.health.health_engine import StrategyHealthEngine
from core.strategy_factory.health.learning.learning_registry import LearningRegistry
from core.strategy_factory.health.learning.health_learning_context import (
    HealthLearningContext,
)
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)
from core.strategy_factory.health.learning.failure_mode_stats import FailureModeStats
from core.strategy_factory.health.death_reason import DeathReason


def test_health_engine_attaches_learning_context_when_available():
    engine = StrategyHealthEngine()
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

    report = engine.evaluate(
        strategy_dna="dna_test",
        performance_metrics={"sharpe": 1.2},
        risk_metrics={"max_drawdown": 0.1, "volatility": 0.2},
        signal_metrics={"entropy": 0.3, "autocorr": 0.1},
        regime_alignment={"trend": 1.0},
        complexity_penalty=0.1,
        learning_registry=registry,
    )

    assert report.learning_context is not None
    assert report.learning_context.lifecycle_snapshot is snapshot
    assert report.learning_context.failure_mode_stats is stats
