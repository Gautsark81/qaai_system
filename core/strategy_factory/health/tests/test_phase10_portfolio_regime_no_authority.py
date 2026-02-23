from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)


def test_portfolio_regime_has_no_authority():
    forbidden = [
        "execute",
        "allocate_capital",
        "promote",
        "demote",
        "override_risk",
        "gate",
    ]

    for attr in forbidden:
        assert not hasattr(PortfolioRegimeDescriptor, attr)
