from datetime import datetime

from core.ssr.components.outcome_quality import OutcomeQualityComponent
from core.ssr.components.health_stability import HealthStabilityComponent
from core.ssr.components.consistency import ConsistencyComponent
from core.strategy_health.contracts.snapshot import StrategyHealthSnapshot
from core.strategy_health.contracts.enums import HealthStatus


def test_outcome_quality_positive():
    comp = OutcomeQualityComponent()
    result = comp.compute(
        inputs={
            "returns": [0.01] * 10,
            "expectancy": 0.01,
            "win_rate": 0.7,
        }
    )
    assert result.score > 0.5


def test_health_stability_mixed():
    snaps = [
        StrategyHealthSnapshot(
            strategy_id="s",
            as_of=datetime.utcnow(),
            overall_score=0.9,
            status=HealthStatus.HEALTHY,
            dimensions={},
            trailing_metrics={},
            regime_context="TREND",
            confidence=0.9,
            flags=[],
            version="v1",
        ),
        StrategyHealthSnapshot(
            strategy_id="s",
            as_of=datetime.utcnow(),
            overall_score=0.4,
            status=HealthStatus.DEGRADED,
            dimensions={},
            trailing_metrics={},
            regime_context="TREND",
            confidence=0.8,
            flags=[],
            version="v1",
        ),
    ]

    comp = HealthStabilityComponent()
    result = comp.compute(inputs={"health_snapshots": snaps})
    assert 0.4 < result.score < 1.0


def test_consistency_low_volatility():
    comp = ConsistencyComponent()
    result = comp.compute(inputs={"returns": [0.01, 0.011, 0.009]})
    assert result.score > 0.8
