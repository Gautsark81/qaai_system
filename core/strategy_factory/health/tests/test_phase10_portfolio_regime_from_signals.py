from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)
from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)


def test_portfolio_regime_uses_cross_strategy_signals_only():
    signals = [
        CrossStrategySignal(
            name="HEALTH_MEAN",
            description="Mean health",
            value=0.62,
            confidence=0.8,
            count=5,
        ),
        CrossStrategySignal(
            name="HEALTH_DISPERSION",
            description="Dispersion of health",
            value=0.12,
            confidence=0.75,
            count=5,
        ),
    ]

    regime = PortfolioRegimeDescriptor.from_signals(signals)

    assert regime.name in {
        "COHERENT",
        "FRAGMENTED",
        "STABLE",
        "UNSTABLE",
    }
