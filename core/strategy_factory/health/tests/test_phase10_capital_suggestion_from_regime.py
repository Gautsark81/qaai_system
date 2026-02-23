from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)
from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)
from core.strategy_factory.health.meta_alpha.capital_suggestion import (
    CapitalSuggestion,
)


def test_capital_suggestion_uses_regime_and_signals_only():
    regime = PortfolioRegimeDescriptor(
        name="COHERENT",
        description="Aligned strategies",
        confidence=0.82,
    )

    signals = [
        CrossStrategySignal(
            name="HEALTH_MEAN",
            description="Mean health",
            value=0.65,
            confidence=0.8,
            count=6,
        )
    ]

    suggestion = CapitalSuggestion.from_context(
        regime=regime,
        signals=signals,
    )

    assert suggestion.name in {
        "RISK_ON",
        "RISK_OFF",
        "NEUTRAL",
    }
