import pytest
from core.institution.portfolio.models import Portfolio
from core.institution.portfolio.registry import PortfolioRegistry


def test_register_and_get_portfolio():
    registry = PortfolioRegistry()

    p = Portfolio(
        portfolio_id="P1",
        name="Core Strategies",
        metadata={"region": "IN"},
    )

    registry.register(portfolio=p)
    fetched = registry.get("P1")

    assert fetched == p


def test_duplicate_portfolio_rejected():
    registry = PortfolioRegistry()

    p = Portfolio(
        portfolio_id="P1",
        name="Alpha",
        metadata={},
    )

    registry.register(portfolio=p)

    with pytest.raises(ValueError):
        registry.register(portfolio=p)


def test_list_all_is_deterministic():
    registry = PortfolioRegistry()

    registry.register(
        portfolio=Portfolio("P2", "Second", {})
    )
    registry.register(
        portfolio=Portfolio("P1", "First", {})
    )

    listed = registry.list_all()

    assert [p.portfolio_id for p in listed] == ["P1", "P2"]
