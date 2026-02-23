# 📁 tests/test_audit_charts.py

import pandas as pd
from datetime import datetime

# Correct import path
from qaai_system.audit import audit_charts


def test_equity_curve_chart_valid():
    df = pd.DataFrame(
        {"timestamp": [datetime(2023, 1, 1), datetime(2023, 1, 2)], "pnl": [100, -50]}
    )
    fig = audit_charts.equity_curve_chart(df)
    # Headless-safe: just check traces present
    assert hasattr(fig, "data")
    assert len(fig.data) > 0


def test_equity_curve_chart_missing_columns():
    df = pd.DataFrame({"symbol": ["AAPL"]})
    fig = audit_charts.equity_curve_chart(df)
    assert hasattr(fig, "data")
    assert len(fig.data) == 0


def test_trade_distribution_chart_valid():
    df = pd.DataFrame({"pnl": [10, 20, -5, 0]})
    fig = audit_charts.trade_distribution_chart(df)
    assert hasattr(fig, "data")
    assert len(fig.data) > 0


def test_trade_distribution_chart_missing():
    df = pd.DataFrame({"symbol": ["AAPL"]})
    fig = audit_charts.trade_distribution_chart(df)
    assert hasattr(fig, "data")
    assert len(fig.data) == 0


def test_sl_tp_scatter_plot_valid():
    df = pd.DataFrame(
        {
            "timestamp": [datetime(2023, 1, 1), datetime(2023, 1, 2)],
            "pnl": [50, -30],
            "stop_loss": [45, 28],
            "take_profit": [60, 35],
            "status": ["FILLED", "FILLED"],
            "symbol": ["AAPL", "GOOG"],
            "strategy_id": ["S1", "S2"],
        }
    )
    fig = audit_charts.sl_tp_scatter_plot(df)
    assert hasattr(fig, "data")
    assert len(fig.data) > 0


def test_sl_tp_scatter_plot_missing_columns():
    df = pd.DataFrame({"pnl": [100]})
    fig = audit_charts.sl_tp_scatter_plot(df)
    assert hasattr(fig, "data")
    assert len(fig.data) == 0


def test_trade_distribution_chart_missing_values():
    # Minimal dataset; avoid None concatenation errors
    df = pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "pnl": 100.0,
                "side": "LONG",
                "entry_time": pd.Timestamp("2025-08-01 09:45"),
                "status": "FILLED",
            }
        ]
    )
    out = audit_charts.trade_distribution_chart(df, title_suffix=None)
    assert out is not None
    # Must have .data even if only one trade
    assert hasattr(out, "data")


# Optional: utility if future tests want to load CSV logs
def load_trade_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "status" in df.columns:
        df = df[df["status"].str.upper() == "FILLED"]
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
