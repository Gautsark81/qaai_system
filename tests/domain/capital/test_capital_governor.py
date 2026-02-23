from domain.capital.capital_governor import CapitalGovernor
from domain.capital.capital_policy import CapitalPolicy
from domain.capital.strategy_capital_state import StrategyCapitalState
from domain.capital.portfolio_exposure import PortfolioExposure


def test_governor_approves_capital():
    gov = CapitalGovernor(
        CapitalPolicy(1_000_000, 0.1, 0.05, 0.2, 0.6)
    )

    strat = StrategyCapitalState("S1", 0, 0.05, 0.8)
    port = PortfolioExposure(0, {})

    cap = gov.approve(strat, port, "NIFTY", 50_000)
    assert cap == 50_000
