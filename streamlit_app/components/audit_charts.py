"""Plot helpers used by tests. Minimal, defensive implementations.
- equity_curve_chart(df)
- trade_distribution_chart(df)
- sl_tp_scatter_plot(df)
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def equity_curve_chart(df: pd.DataFrame) -> go.Figure:
    """Return a line chart of cumulative PnL over time.
    If required columns missing, return empty figure (tests expect empty chart behavior).
    """
    if not isinstance(df, pd.DataFrame):
        return go.Figure()
    if not {"timestamp", "pnl"}.issubset(df.columns):
        return go.Figure()

    out = df.copy()
    out = out.sort_values("timestamp")
    out["cum_pnl"] = out["pnl"].cumsum()
    fig = px.line(out, x="timestamp", y="cum_pnl", title="Equity Curve")
    return fig


def trade_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Histogram of pnl. If pnl missing return empty figure (no data in fig.data).
    Tests expect an empty chart when pnl column missing.
    """
    fig = go.Figure()
    if not isinstance(df, pd.DataFrame):
        return fig
    if "pnl" not in df.columns:
        # empty figure
        return fig

    try:
        fig = px.histogram(df, x="pnl", nbins=20, title="PnL")
    except Exception:
        return go.Figure()
    return fig


def sl_tp_scatter_plot(df: pd.DataFrame) -> go.Figure:
    """Scatter plot of stops vs profits colored by status.
    If required columns are missing, return empty figure.
    """
    required = {"stop_loss", "take_profit", "pnl", "status"}
    if not isinstance(df, pd.DataFrame):
        return go.Figure()
    if not required.issubset(df.columns):
        return go.Figure()

    fig = px.scatter(
        df,
        x="stop_loss",
        y="take_profit",
        color="status",
        hover_data=["pnl", "symbol", "strategy_id"],
        title="SL vs TP",
    )
    return fig
