# tests/strategy_factory/capital/test_capital_metrics.py

from core.strategy_factory.capital.capital_metrics import (
    CapitalStabilitySnapshot,
    CapitalMetricsComputer,
    StabilityScoreCalculator,
)


# ============================================================
# HELPERS
# ============================================================

def _stable_snapshot():
    return CapitalStabilitySnapshot(
        total_capital=1_000_000,
        gross_exposure=650_000,
        max_envelope=1_000_000,
        strategy_capital_allocations={
            "s1": 300_000,
            "s2": 200_000,
            "s3": 150_000,
        },
        correlated_exposure=150_000,
        modeled_exposure=650_000,
        realized_exposure=645_000,
        throttle_activations=1,
        total_execution_cycles=100,
        promotions=1,
        demotions=1,
        total_strategies=10,
    )


# ============================================================
# 1️⃣ Stable Capital Scenario
# ============================================================

def test_stable_capital_scenario_high_score():
    current = _stable_snapshot()
    previous = _stable_snapshot()

    metrics = CapitalMetricsComputer.compute(current, previous)
    score = StabilityScoreCalculator.compute(metrics)

    assert score.composite_score >= 80


# ============================================================
# 2️⃣ Envelope Overshoot Scenario
# ============================================================

def test_envelope_overshoot_penalized():
    snap = _stable_snapshot()

    overshoot = CapitalStabilitySnapshot(
        **{
            **snap.__dict__,
            "gross_exposure": 1_200_000,  # exceeds envelope
        }
    )

    metrics = CapitalMetricsComputer.compute(overshoot, snap)
    score = StabilityScoreCalculator.compute(metrics)

    assert score.exposure_score < 50
    assert score.composite_score < 70


# ============================================================
# 3️⃣ Correlated Cluster Overflow
# ============================================================

def test_correlated_exposure_penalized():
    snap = _stable_snapshot()

    correlated = CapitalStabilitySnapshot(
        **{
            **snap.__dict__,
            "correlated_exposure": 600_000,
        }
    )

    metrics = CapitalMetricsComputer.compute(correlated, snap)
    score = StabilityScoreCalculator.compute(metrics)

    assert score.interaction_score < 60


# ============================================================
# 4️⃣ High Strategy Churn
# ============================================================

def test_high_strategy_churn_penalized():
    snap = _stable_snapshot()

    churn = CapitalStabilitySnapshot(
        **{
            **snap.__dict__,
            "promotions": 5,
            "demotions": 5,
        }
    )

    metrics = CapitalMetricsComputer.compute(churn, snap)
    score = StabilityScoreCalculator.compute(metrics)

    assert score.interaction_score < 70


# ============================================================
# 5️⃣ Drift Divergence Scenario
# ============================================================

def test_realized_vs_modeled_drift_penalized():
    snap = _stable_snapshot()

    drift = CapitalStabilitySnapshot(
        **{
            **snap.__dict__,
            "realized_exposure": 800_000,
        }
    )

    metrics = CapitalMetricsComputer.compute(drift, snap)
    score = StabilityScoreCalculator.compute(metrics)

    assert score.drift_score < 60


# ============================================================
# 6️⃣ Governance Over-Trigger Scenario
# ============================================================

def test_throttle_overactivation_penalized():
    snap = _stable_snapshot()

    over_throttle = CapitalStabilitySnapshot(
        **{
            **snap.__dict__,
            "throttle_activations": 50,
            "total_execution_cycles": 100,
        }
    )

    metrics = CapitalMetricsComputer.compute(over_throttle, snap)
    score = StabilityScoreCalculator.compute(metrics)

    assert score.governance_score < 60


# ============================================================
# Determinism Test
# ============================================================

def test_metric_computation_is_deterministic():
    current = _stable_snapshot()
    previous = _stable_snapshot()

    m1 = CapitalMetricsComputer.compute(current, previous)
    m2 = CapitalMetricsComputer.compute(current, previous)

    assert m1 == m2

    s1 = StabilityScoreCalculator.compute(m1)
    s2 = StabilityScoreCalculator.compute(m2)

    assert s1 == s2