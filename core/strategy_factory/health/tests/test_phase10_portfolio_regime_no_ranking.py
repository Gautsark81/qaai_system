from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)


def test_portfolio_regime_has_no_ranking_or_selection():
    forbidden = [
        "rank",
        "select",
        "optimize",
        "allocate",
        "vote",
    ]

    for attr in forbidden:
        assert not hasattr(PortfolioRegimeDescriptor, attr)
