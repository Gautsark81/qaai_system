import pytest
from datetime import datetime

from core.strategy_health.contracts.enums import HealthStatus, DimensionVerdict
from core.strategy_health.contracts.flags import HealthFlag
from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.snapshot import StrategyHealthSnapshot


def test_enums_are_stable():
    assert HealthStatus.HEALTHY.value == "HEALTHY"
    assert HealthStatus.DEGRADED.value == "DEGRADED"
    assert DimensionVerdict.FAIL.value == "FAIL"


def test_health_flag_is_frozen():
    flag = HealthFlag(
        code="TEST",
        severity="HIGH",
        message="Test message",
        dimension="PERFORMANCE",
    )

    with pytest.raises(Exception):
        flag.code = "MUTATE"


def test_dimension_score_bounds_enforced():
    with pytest.raises(ValueError):
        HealthDimensionScore(
            name="performance",
            score=1.5,
            weight=0.3,
            metrics={},
            verdict=DimensionVerdict.FAIL,
        )


def test_snapshot_bounds_enforced():
    dim = HealthDimensionScore(
        name="performance",
        score=0.8,
        weight=1.0,
        metrics={"sharpe": 1.2},
        verdict=DimensionVerdict.PASS,
    )

    with pytest.raises(ValueError):
        StrategyHealthSnapshot(
            strategy_id="s1",
            as_of=datetime.utcnow(),
            overall_score=1.2,
            status=HealthStatus.HEALTHY,
            dimensions={"performance": dim},
            trailing_metrics={},
            regime_context="TREND_LOW_VOL",
            confidence=0.9,
            flags=[],
            version="v1",
        )


def test_snapshot_is_frozen():
    dim = HealthDimensionScore(
        name="performance",
        score=0.7,
        weight=1.0,
        metrics={},
        verdict=DimensionVerdict.WARN,
    )

    snapshot = StrategyHealthSnapshot(
        strategy_id="s1",
        as_of=datetime.utcnow(),
        overall_score=0.7,
        status=HealthStatus.DEGRADED,
        dimensions={"performance": dim},
        trailing_metrics={},
        regime_context="RANGE",
        confidence=0.6,
        flags=[],
        version="v1",
    )

    with pytest.raises(Exception):
        snapshot.status = HealthStatus.HEALTHY
