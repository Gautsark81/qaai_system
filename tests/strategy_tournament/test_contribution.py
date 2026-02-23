from modules.strategy_tournament.contribution import compute_contribution
from modules.strategy_tournament.metrics import SymbolMetrics
from modules.strategy_tournament.portfolio_state import PortfolioState


def test_positive_contribution():
    base = PortfolioState({})
    candidate = [
        SymbolMetrics("A", 10, 6, 4, 0.6, 100, 3),
    ]

    c = compute_contribution(base, candidate, max_dd_threshold=5)
    assert c.delta_ssr > 0
