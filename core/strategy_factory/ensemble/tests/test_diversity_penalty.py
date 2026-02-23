from core.strategy_factory.ensemble import EnsembleSnapshot


def test_diversity_penalty_validation():
    snap = EnsembleSnapshot(
        strategies=[],
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        diversity_penalty_strength=0.5,
    )

    assert snap.diversity_penalty_strength == 0.5