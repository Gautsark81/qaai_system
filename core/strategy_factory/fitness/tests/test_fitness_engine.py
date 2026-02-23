from core.strategy_factory.fitness.contracts import FitnessInputs
from core.strategy_factory.fitness.fitness_engine import FitnessEngine


def test_fitness_blocks_fragile_strategy():
    inputs = FitnessInputs(
        sharpe=2.5,
        win_rate=0.65,
        max_drawdown=0.3,
        trade_count=80,
        regime_consistency=0.4,
        tail_loss_ratio=3.5,
    )

    result = FitnessEngine.compute(inputs)

    assert result.raw_fitness > 0.5
    assert result.final_fitness < result.raw_fitness
    assert result.is_capital_eligible is False


def test_fitness_allows_stable_strategy():
    inputs = FitnessInputs(
        sharpe=1.8,
        win_rate=0.58,
        max_drawdown=0.1,
        trade_count=120,
        regime_consistency=0.85,
        tail_loss_ratio=1.4,
    )

    result = FitnessEngine.compute(inputs)

    assert result.final_fitness >= 0.6
    assert result.is_capital_eligible is True
