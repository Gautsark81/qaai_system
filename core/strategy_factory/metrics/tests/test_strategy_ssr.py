from core.strategy_factory.metrics.strategy_metrics import compute_strategy_ssr


def test_strategy_ssr_computation():
    """
    Strategy Success Ratio (SSR) must be
    computed deterministically.
    """

    trades = [
        {"pnl": 10},
        {"pnl": -5},
        {"pnl": 15},
        {"pnl": -2},
        {"pnl": 8},
    ]

    # Wins: 3 / 5
    assert compute_strategy_ssr(trades) == 0.6
