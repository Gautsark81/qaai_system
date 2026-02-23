import plotly.graph_objects as go
import streamlit as st


def plot_signal_chart(ohlcv_df, signals_df, symbol):
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=ohlcv_df.index,
            open=ohlcv_df["open"],
            high=ohlcv_df["high"],
            low=ohlcv_df["low"],
            close=ohlcv_df["close"],
            name="Price",
        )
    )

    if not signals_df.empty:
        buy_signals = signals_df[signals_df["signal"] == "BUY"]
        sell_signals = signals_df[signals_df["signal"] == "SELL"]

        fig.add_trace(
            go.Scatter(
                x=buy_signals["timestamp"],
                y=(
                    buy_signals["price"]
                    if "price" in buy_signals
                    else ohlcv_df.loc[buy_signals["timestamp"]]["close"]
                ),
                mode="markers",
                marker=dict(symbol="triangle-up", color="green", size=10),
                name="BUY",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=sell_signals["timestamp"],
                y=(
                    sell_signals["price"]
                    if "price" in sell_signals
                    else ohlcv_df.loc[sell_signals["timestamp"]]["close"]
                ),
                mode="markers",
                marker=dict(symbol="triangle-down", color="red", size=10),
                name="SELL",
            )
        )

    fig.update_layout(
        title=f"Signal Chart for {symbol}",
        xaxis_title="Timestamp",
        yaxis_title="Price",
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)


def draw_sidebar(symbols_available):
    st.sidebar.header("🧭 Navigation & Filters")

    mode = st.sidebar.radio("Select Mode", ["Signal Viewer", "Backtest"])
    selected_symbols = st.sidebar.multiselect(
        "Select Symbols", options=symbols_available, default=symbols_available[:1]
    )
    timeframe = st.sidebar.selectbox("Timeframe", ["5min", "15min", "1h"])
    confidence = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    visualize = st.sidebar.checkbox("Show Backtest Chart", value=True)

    return selected_symbols, mode, visualize, confidence, timeframe


def filter_signals(signals_df, threshold):
    """Filter signals based on confidence score."""
    if "confidence" in signals_df.columns:
        return signals_df[signals_df["confidence"] >= threshold]
    return signals_df
