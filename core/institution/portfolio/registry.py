# core/institution/portfolio/registry.py
from typing import Dict, List
from core.institution.portfolio.models import Portfolio


class PortfolioRegistry:
    """
    Registry for multi-portfolio governance.

    HARD RULE:
    - Portfolios are isolated.
    """

    def __init__(self):
        self._portfolios: Dict[str, Portfolio] = {}

    def register(self, *, portfolio: Portfolio) -> None:
        if portfolio.portfolio_id in self._portfolios:
            raise ValueError("portfolio already registered")
        self._portfolios[portfolio.portfolio_id] = portfolio

    def get(self, portfolio_id: str) -> Portfolio:
        return self._portfolios[portfolio_id]

    def list_all(self) -> List[Portfolio]:
        return sorted(
            self._portfolios.values(),
            key=lambda p: p.portfolio_id,
        )
