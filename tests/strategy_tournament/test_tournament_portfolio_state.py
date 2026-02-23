from modules.strategy_tournament.portfolio_state import PortfolioState


def test_portfolio_state_empty():
    p = PortfolioState({})
    assert p.total_pnl == 0
    assert p.max_drawdown == 0
