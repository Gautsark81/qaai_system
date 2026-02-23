import pytest
from datetime import datetime

from core.strategy_health.aggregator import StrategyHealthAggregator
from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.enums import DimensionVerdict, HealthStatus
from core.strategy_health.contracts.snapshot import StrategyHealthSnapshot


def _dim(name, score, verdict, weight=1.0):
    return HealthDimensionScore(
        name=name,
        score=score,
        weight=weight,
        metrics={},
        verdict=verdict,
    )


def test_healthy_strategy():
    agg = StrategyHealthAggregator()

    snapshot = agg.aggregate(
        strategy_id="s1",
        as_of=datetime.utcnow(),
        dimensions=[
            _dim("performance", 0.8, DimensionVerdict.PASS),
            _dim("risk", 0.9, DimensionVerdict.PASS),
        ],
        trailing_metrics={},
        regime_context="TREND",
        confidence=0.9,
        version="v1",
    )

    assert snapshot.status == HealthStatus.HEALTHY
    assert snapshot.overall_score == pytest.approx(0.85, rel=1e-4)
    assert snapshot.flags == []


def test_single_warn_still_healthy():
    agg = StrategyHealthAggregator()

    snapshot = agg.aggregate(
        strategy_id="s2",
        as_of=datetime.utcnow(),
        dimensions=[
            _dim("performance", 0.6, DimensionVerdict.WARN),
            _dim("risk", 0.9, DimensionVerdict.PASS),
        ],
        trailing_metrics={},
        regime_context="RANGE",
        confidence=0.8,
        version="v1",
    )

    assert snapshot.status == HealthStatus.HEALTHY
    assert len(snapshot.flags) == 1


def test_two_warns_degraded():
    agg = StrategyHealthAggregator()

    snapshot = agg.aggregate(
        strategy_id="s3",
        as_of=datetime.utcnow(),
        dimensions=[
            _dim("performance", 0.6, DimensionVerdict.WARN),
            _dim("risk", 0.7, DimensionVerdict.WARN),
            _dim("execution", 0.9, DimensionVerdict.PASS),
        ],
        trailing_metrics={},
        regime_context="RANGE",
        confidence=0.7,
        version="v1",
    )

    assert snapshot.status == HealthStatus.DEGRADED
    assert len(snapshot.flags) == 2


def test_any_fail_is_critical():
    agg = StrategyHealthAggregator()

    snapshot = agg.aggregate(
        strategy_id="s4",
        as_of=datetime.utcnow(),
        dimensions=[
            _dim("performance", 0.2, DimensionVerdict.FAIL),
            _dim("risk", 0.9, DimensionVerdict.PASS),
        ],
        trailing_metrics={},
        regime_context="VOLATILE",
        confidence=0.6,
        version="v1",
    )

    assert snapshot.status == HealthStatus.CRITICAL
    assert any("FAIL" in f.code for f in snapshot.flags)


def test_weighted_score_calculation():
    agg = StrategyHealthAggregator()

    snapshot = agg.aggregate(
        strategy_id="s5",
        as_of=datetime.utcnow(),
        dimensions=[
            _dim("performance", 1.0, DimensionVerdict.PASS, weight=2.0),
            _dim("risk", 0.0, DimensionVerdict.PASS, weight=1.0),
        ],
        trailing_metrics={},
        regime_context="TREND",
        confidence=1.0,
        version="v1",
    )

    assert snapshot.overall_score == pytest.approx(0.6667, rel=1e-4)


def test_empty_dimensions_rejected():
    agg = StrategyHealthAggregator()

    with pytest.raises(ValueError):
        agg.aggregate(
            strategy_id="s6",
            as_of=datetime.utcnow(),
            dimensions=[],
            trailing_metrics={},
            regime_context="NONE",
            confidence=0.5,
            version="v1",
        )


def test_zero_weight_rejected():
    agg = StrategyHealthAggregator()

    with pytest.raises(ValueError):
        agg.aggregate(
            strategy_id="s7",
            as_of=datetime.utcnow(),
            dimensions=[
                _dim("performance", 0.5, DimensionVerdict.PASS, weight=0.0)
            ],
            trailing_metrics={},
            regime_context="NONE",
            confidence=0.5,
            version="v1",
        )


def test_deterministic_dimension_ordering():
    agg = StrategyHealthAggregator()

    snapshot = agg.aggregate(
        strategy_id="s8",
        as_of=datetime.utcnow(),
        dimensions=[
            _dim("risk", 0.9, DimensionVerdict.PASS),
            _dim("performance", 0.8, DimensionVerdict.PASS),
        ],
        trailing_metrics={},
        regime_context="TREND",
        confidence=0.9,
        version="v1",
    )

    assert list(snapshot.dimensions.keys()) == ["performance", "risk"]
