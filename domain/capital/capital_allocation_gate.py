from domain.capital.capital_policy import CapitalPolicy
from domain.capital.strategy_capital_state import StrategyCapitalState
from domain.capital.portfolio_exposure import PortfolioExposure


class CapitalAllocationGate:
    """
    Decides whether capital may be allocated.
    """

    @staticmethod
    def allow(
        policy: CapitalPolicy,
        strategy: StrategyCapitalState,
        portfolio: PortfolioExposure,
        symbol: str,
        requested_capital: float,
    ) -> bool:

        if strategy.ssr < policy.min_ssr:
            return False

        if strategy.current_drawdown_pct > policy.max_drawdown_pct:
            return False

        if requested_capital > policy.max_total_capital * policy.max_per_strategy_pct:
            return False

        symbol_cap = portfolio.per_symbol.get(symbol, 0.0)
        if symbol_cap + requested_capital > policy.max_total_capital * policy.max_per_symbol_pct:
            return False

        return True
