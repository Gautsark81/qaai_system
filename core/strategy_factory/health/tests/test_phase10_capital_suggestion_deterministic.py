from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)
from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)
from core.strategy_factory.health.meta_alpha.capital_suggestion import (
    CapitalSuggestion,
)


def test_capital_suggestion_is_deterministic():
    regime = PortfolioRegimeDescriptor(
        name="FRAGMENTED",
        description="Divergent strategies",
        confidence=0.75,
    )

    signals = [
        CrossStrategySignal(
            name="HEALTH_MEAN",
            description="Mean health",
            value=0.35,
            confidence=0.7,
            count=5,
        )
    ]

    s1 = CapitalSuggestion.from_context(regime=regime, signals=signals)
    s2 = CapitalSuggestion.from_context(regime=regime, signals=signals)

    assert s1.name == s2.name
    assert s1.confidence == s2.confidence
