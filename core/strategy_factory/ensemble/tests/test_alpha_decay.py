from core.strategy_factory.ensemble.alpha_decay import (
    AlphaDecayEngine,
)


def test_alpha_decay_detects_deterioration():

    returns = {
        "DECAYING": [0.02, 0.02, 0.015, 0.01, 0.005, -0.01],
        "HEALTHY": [0.01, 0.012, 0.013, 0.014, 0.015, 0.016],
    }

    result = AlphaDecayEngine.evaluate(returns)

    assert result.decay_flags["DECAYING"] is True
    assert result.decay_flags["HEALTHY"] is False