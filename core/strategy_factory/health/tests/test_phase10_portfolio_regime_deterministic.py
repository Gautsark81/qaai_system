from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)
from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)


def test_portfolio_regime_descriptor_is_deterministic():
    signals = [
        CrossStrategySignal(
            name="HEALTH_MEAN",
            description="Mean health",
            value=0.6,
            confidence=0.8,
            count=4,
        ),
        CrossStrategySignal(
            name="HEALTH_DISPERSION",
            description="Dispersion",
            value=0.2,
            confidence=0.75,
            count=4,
        ),
    ]

    r1 = PortfolioRegimeDescriptor.from_signals(signals)
    r2 = PortfolioRegimeDescriptor.from_signals(signals)

    assert r1.name == r2.name
    assert r1.confidence == r2.confidence
