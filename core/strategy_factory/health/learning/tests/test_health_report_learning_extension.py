from datetime import datetime, timezone

from core.strategy_factory.health.artifacts import HealthReport
from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
from core.strategy_factory.health.learning.health_learning_context import (
    HealthLearningContext,
)


def test_health_report_accepts_learning_context():
    snapshot = StrategyHealthSnapshot(
        strategy_dna="dna_x",
        timestamp=datetime.now(timezone.utc),
        health_score=0.55,
        confidence=0.7,
        decay_risk=0.2,
        performance_metrics={},
        risk_metrics={},
        signal_metrics={},
        regime_alignment={},
        flags=[],
    )

    ctx = HealthLearningContext(
        lifecycle_snapshot=None,
        failure_mode_stats=None,
    )

    report = HealthReport(
        snapshot=snapshot,
        inputs_hash="abc123",
        learning_context=ctx,
    )

    assert report.learning_context is ctx


def test_health_report_learning_context_optional():
    snapshot = StrategyHealthSnapshot(
        strategy_dna="dna_y",
        timestamp=datetime.now(timezone.utc),
        health_score=0.9,
        confidence=0.95,
        decay_risk=0.1,
        performance_metrics={},
        risk_metrics={},
        signal_metrics={},
        regime_alignment={},
        flags=[],
    )

    report = HealthReport(
        snapshot=snapshot,
        inputs_hash="xyz789",
    )

    assert report.learning_context is None
