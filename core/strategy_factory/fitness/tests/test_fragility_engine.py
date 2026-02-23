from core.strategy_factory.fitness.contracts import FitnessInputs
from core.strategy_factory.fitness.fragility_engine import FragilityEngine


def test_fragility_high_tail_loss():
    inputs = FitnessInputs(
        sharpe=1.5,
        win_rate=0.55,
        max_drawdown=0.1,
        trade_count=100,
        regime_consistency=0.8,
        tail_loss_ratio=4.0,
    )

    penalty = FragilityEngine.compute(inputs)
    assert penalty >= 0.4


def test_fragility_low_sample_penalty():
    inputs = FitnessInputs(
        sharpe=1.2,
        win_rate=0.6,
        max_drawdown=0.1,
        trade_count=20,
        regime_consistency=0.9,
        tail_loss_ratio=1.5,
    )

    penalty = FragilityEngine.compute(inputs)
    assert penalty >= 0.2
