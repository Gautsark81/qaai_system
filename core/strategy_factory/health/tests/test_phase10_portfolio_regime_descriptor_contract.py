from core.strategy_factory.health.meta_alpha.portfolio_regime import (
    PortfolioRegimeDescriptor,
)


def test_portfolio_regime_descriptor_is_descriptive():
    regime = PortfolioRegimeDescriptor(
        name="COHERENT",
        description="Strategies show aligned health and low dispersion",
        confidence=0.82,
    )

    assert regime.name == "COHERENT"
    assert isinstance(regime.description, str)
    assert regime.advisory_only is True
