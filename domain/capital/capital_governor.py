from domain.capital.capital_allocation_gate import CapitalAllocationGate
from domain.capital.capital_policy import CapitalPolicy
from domain.capital.strategy_capital_state import StrategyCapitalState
from domain.capital.portfolio_exposure import PortfolioExposure


class CapitalGovernor:
    """
    Final authority on position sizing.
    """

    def __init__(self, policy: CapitalPolicy):
        self.policy = policy

    def approve(
        self,
        strategy: StrategyCapitalState,
        portfolio: PortfolioExposure,
        symbol: str,
        requested_capital: float,
    ) -> float | None:

        allowed = CapitalAllocationGate.allow(
            self.policy,
            strategy,
            portfolio,
            symbol,
            requested_capital,
        )

        return requested_capital if allowed else None
