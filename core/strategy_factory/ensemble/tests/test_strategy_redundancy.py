from core.strategy_factory.ensemble.strategy_diversity import (
    StrategyDiversityEngine,
)
from core.strategy_factory.ensemble.strategy_redundancy import (
    StrategyRedundancyEngine,
)


def test_redundancy_detection():
    returns = {
        "A": [0.01, 0.02, 0.03, 0.04],
        "B": [0.01, 0.02, 0.03, 0.04],  # perfectly correlated
        "C": [-0.01, -0.02, -0.03, -0.04],  # perfectly negatively correlated
    }

    diversity = StrategyDiversityEngine.evaluate(returns)

    redundancy = StrategyRedundancyEngine.evaluate(
        diversity.correlation_matrix,
        threshold=0.9,
    )

    assert len(redundancy.redundant_pairs) >= 1
    assert redundancy.redundancy_score > 0