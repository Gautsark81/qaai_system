from core.strategy_factory.ensemble.strategy_diversity import (
    StrategyDiversityEngine,
)


def test_strategy_diversity_basic():
    returns = {
        "A": [0.01, 0.02, 0.015, -0.01],
        "B": [0.02, 0.01, 0.018, -0.015],
        "C": [-0.01, -0.02, -0.015, 0.01],
    }

    result = StrategyDiversityEngine.evaluate(returns)

    assert isinstance(result.ensemble_diversity_score, float)
    assert "A" in result.correlation_matrix
    assert "B" in result.correlation_matrix["A"]