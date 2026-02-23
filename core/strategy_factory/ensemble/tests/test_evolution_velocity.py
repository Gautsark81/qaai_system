from core.strategy_factory.ensemble.evolution_velocity import EvolutionVelocityEngine


def test_evolution_velocity_trends():

    retirement_history = [0, 1, 2]
    activation_history = [0, 1, 1]
    decay_history = [0.2, 0.3, 0.4]
    stability_history = [0.9, 0.8, 0.7]

    result = EvolutionVelocityEngine.evaluate(
        retirement_history,
        activation_history,
        decay_history,
        stability_history,
    )

    assert result.retirement_rate > 0
    assert result.activation_rate >= 0
    assert result.avg_decay_trend > 0
    assert result.stability_trend < 0