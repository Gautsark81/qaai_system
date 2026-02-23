from domain.capital.capital_allocation_gate import CapitalAllocationGate
from domain.capital.capital_policy import CapitalPolicy
from domain.capital.strategy_capital_state import StrategyCapitalState
from domain.capital.portfolio_exposure import PortfolioExposure


def test_capital_gate_blocks_low_ssr():
    policy = CapitalPolicy(1_000_000, 0.1, 0.05, 0.2, 0.7)
    strat = StrategyCapitalState("S1", 0, 0.01, 0.5)
    port = PortfolioExposure(0, {})

    assert CapitalAllocationGate.allow(
        policy, strat, port, "NIFTY", 50_000
    ) is False
