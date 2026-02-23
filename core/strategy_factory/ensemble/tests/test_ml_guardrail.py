from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
)
from core.strategy_factory.ensemble.ml_guardrail import MLDriftGuardrail


def test_ml_guardrail_runs():
    strategies = [
        EnsembleStrategy("A", 95, 2),
        EnsembleStrategy("B", 85, 10),
    ]

    snap = EnsembleSnapshot(
        strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        meta_ml_enabled=True,
        meta_ml_max_total_drift_pct=0.5,   # loose threshold
        meta_ml_max_single_drift_pct=0.5,
    )

    guard = MLDriftGuardrail.evaluate(snap)

    assert isinstance(guard.ml_allowed, bool)