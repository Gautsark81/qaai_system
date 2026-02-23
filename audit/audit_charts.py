# 📁 qaai_system/audit/audit_charts.py

from __future__ import annotations

import pandas as pd
import plotly.express as px


def equity_curve_chart(df: pd.DataFrame):
    """
    Plot equity curve (PnL over time).
    Expects df with columns ['timestamp', 'pnl'].
    Returns a Plotly Figure (empty if required columns missing).
    """
    if df is None or df.empty or not {"timestamp", "pnl"}.issubset(df.columns):
        return px.scatter(pd.DataFrame())  # return empty fig

    # Ensure timestamp is datetime
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return px.line(df, x="timestamp", y="pnl", title="Equity Curve")


def trade_distribution_chart(df: pd.DataFrame, title_suffix: str | None = ""):
    """
    Plot histogram of trade PnL distribution.
    Expects df with column ['pnl'].
    """
    if df is None or df.empty or "pnl" not in df.columns:
        return px.histogram(pd.DataFrame())  # empty fig

    title = "Trade Distribution"
    if title_suffix:
        title += f" {title_suffix}"

    return px.histogram(df, x="pnl", nbins=20, title=title)


def sl_tp_scatter_plot(df: pd.DataFrame):
    """
    Scatter plot of Stop Loss vs Take Profit with trade info.
    Requires columns:
        ['timestamp', 'pnl', 'stop_loss', 'take_profit', 'status', 'symbol', 'strategy_id']
    """
    required = {
        "timestamp",
        "pnl",
        "stop_loss",
        "take_profit",
        "status",
        "symbol",
        "strategy_id",
    }
    if df is None or df.empty or not required.issubset(df.columns):
        return px.scatter(pd.DataFrame())  # empty fig

    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return px.scatter(
        df,
        x="stop_loss",
        y="take_profit",
        color="status",
        hover_data=["symbol", "strategy_id", "pnl", "timestamp"],
        title="Stop Loss vs Take Profit Scatter",
    )
