from datetime import datetime, timezone

from core.strategy_factory.health.learning.death_pattern_aggregator import (
    DeathPatternAggregator,
)
from core.strategy_factory.health.death_attribution import DeathAttribution
from core.strategy_factory.health.death_reason import DeathReason
from core.strategy_factory.health.learning.lifecycle_learning_snapshot import (
    LifecycleLearningSnapshot,
)


def test_death_pattern_aggregator_empty():
    aggregator = DeathPatternAggregator()

    snapshot = aggregator.aggregate(
        events=[],
        total_strategies_observed=0,
        timestamp=datetime.now(timezone.utc),
    )

    assert isinstance(snapshot, LifecycleLearningSnapshot)
    assert snapshot.total_deaths == 0
    assert snapshot.death_reason_counts == {}


def test_death_pattern_aggregator_counts_reasons():
    now = datetime.now(timezone.utc)

    events = [
        DeathAttribution(
            strategy_id="s1",
            reason=DeathReason.MAX_DRAWDOWN,
            timestamp=now,
            triggered_by="health_engine",
            metrics={},
        ),
        DeathAttribution(
            strategy_id="s2",
            reason=DeathReason.SSR_FAILURE,
            timestamp=now,
            triggered_by="fitness_monitor",
            metrics={},
        ),
        DeathAttribution(
            strategy_id="s3",
            reason=DeathReason.MAX_DRAWDOWN,
            timestamp=now,
            triggered_by="health_engine",
            metrics={},
        ),
    ]

    aggregator = DeathPatternAggregator()

    snapshot = aggregator.aggregate(
        events=events,
        total_strategies_observed=10,
        timestamp=now,
    )

    assert snapshot.total_deaths == 3
    assert snapshot.death_reason_counts[DeathReason.MAX_DRAWDOWN] == 2
    assert snapshot.death_reason_counts[DeathReason.SSR_FAILURE] == 1
    assert snapshot.total_strategies_observed == 10


def test_death_pattern_aggregator_is_deterministic():
    now = datetime.now(timezone.utc)

    events = [
        DeathAttribution(
            strategy_id="s1",
            reason=DeathReason.OPERATOR_KILL,
            timestamp=now,
            triggered_by="operator",
            metrics={},
        )
    ]

    aggregator = DeathPatternAggregator()

    snap1 = aggregator.aggregate(
        events=events,
        total_strategies_observed=1,
        timestamp=now,
    )
    snap2 = aggregator.aggregate(
        events=events,
        total_strategies_observed=1,
        timestamp=now,
    )

    assert snap1 == snap2
