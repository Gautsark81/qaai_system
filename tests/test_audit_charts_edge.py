# 📁 tests/test_audit_charts_edge.py

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from qaai_system.audit import audit_charts


def test_equity_curve_chart_empty_df():
    df = pd.DataFrame()
    fig = audit_charts.equity_curve_chart(df)
    assert fig is not None
    assert not fig.data, "Chart should be empty for empty DataFrame"


def test_equity_curve_chart_with_nans():
    df = pd.DataFrame(
        {
            "timestamp": [datetime(2023, 1, 1), datetime(2023, 1, 2)],
            "pnl": [np.nan, 200],
        }
    )
    fig = audit_charts.equity_curve_chart(df)
    assert fig is not None
    assert fig.data, "Chart should handle NaN values gracefully"


def test_trade_distribution_chart_large_input():
    df = pd.DataFrame({"pnl": np.random.randn(10_000)})
    fig = audit_charts.trade_distribution_chart(df)
    assert fig is not None
    assert fig.data, "Chart should handle very large DataFrames"


def test_sl_tp_scatter_plot_with_missing_values():
    df = pd.DataFrame(
        {
            "timestamp": [datetime(2023, 1, 1), datetime(2023, 1, 2)],
            "pnl": [50, None],
            "stop_loss": [45, None],
            "take_profit": [60, None],
            "status": ["FILLED", None],
            "symbol": ["AAPL", None],
            "strategy_id": ["S1", None],
        }
    )
    fig = audit_charts.sl_tp_scatter_plot(df)
    assert fig is not None
    # At least one trace should exist for valid row
    assert any(len(trace.x) > 0 for trace in fig.data)


def test_sl_tp_scatter_plot_large_input():
    n = 5000
    df = pd.DataFrame(
        {
            "timestamp": [
                datetime(2023, 1, 1) + timedelta(minutes=i) for i in range(n)
            ],
            "pnl": np.random.randn(n),
            "stop_loss": np.random.uniform(90, 110, n),
            "take_profit": np.random.uniform(110, 130, n),
            "status": ["FILLED"] * n,
            "symbol": ["SYM"] * n,
            "strategy_id": ["S1"] * n,
        }
    )
    fig = audit_charts.sl_tp_scatter_plot(df)
    assert fig is not None
    assert fig.data, "Scatter should handle thousands of points"
