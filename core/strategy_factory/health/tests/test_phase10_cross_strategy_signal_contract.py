from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)


def test_cross_strategy_signal_is_descriptive():
    signal = CrossStrategySignal(
        name="HEALTH_BREADTH",
        description="Proportion of strategies in healthy state",
        value=0.65,
        confidence=0.8,
    )

    assert signal.name == "HEALTH_BREADTH"
    assert isinstance(signal.value, float)
    assert signal.advisory_only is True
