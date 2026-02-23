import pytest
from core.strategy_factory.ensemble import EnsembleStrategy, EnsembleSnapshot


def test_invalid_meta_weights_sum():
    strategies = [EnsembleStrategy("A", 90, 0)]

    with pytest.raises(ValueError):
        EnsembleSnapshot(
            strategies,
            available_capital=1000,
            global_cap=1000,
            per_strategy_cap=1000,
            concentration_cap=1000,
            meta_ssr_weight=0.5,
            meta_drawdown_weight=0.5,
            meta_capital_eff_weight=0.5,  # invalid sum
        )


def test_meta_weights_valid():
    strategies = [EnsembleStrategy("A", 90, 0)]

    snap = EnsembleSnapshot(
        strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        meta_ssr_weight=0.3,
        meta_drawdown_weight=0.25,
        meta_capital_eff_weight=0.2,
        meta_governance_weight=0.15,
        meta_concentration_weight=0.1,
    )

    assert snap.meta_ssr_weight == 0.3