from modules.portfolio.metrics import PortfolioMetricsEngine


def test_equity_curve():
    equities = [100, 105, 102]
    curve = PortfolioMetricsEngine.equity_curve(equities)

    assert len(curve) == 3
    assert curve[0].equity == 100
    assert curve[2].equity == 102


def test_drawdown_monotonicity():
    equities = [100, 110, 105, 120, 90]
    dds = PortfolioMetricsEngine.drawdowns(equities)

    # Peak at 110 → drawdown at 105
    assert dds[2].drawdown_abs == 5

    # New peak resets drawdown
    assert dds[3].drawdown_abs == 0

    # Largest drawdown
    assert dds[4].drawdown_abs == 30
    assert round(dds[4].drawdown_pct, 2) == 0.25


def test_rolling_returns():
    equities = [100, 105, 110, 120]
    rets = PortfolioMetricsEngine.rolling_returns(equities, window=2)

    assert len(rets) == 2
    assert round(rets[0], 2) == 0.10
    assert round(rets[1], 2) == 0.14


def test_rolling_volatility():
    returns = [0.1, 0.2, 0.0, 0.1]
    vols = PortfolioMetricsEngine.rolling_volatility(returns, window=2)

    assert len(vols) == 3
    assert all(v >= 0 for v in vols)
