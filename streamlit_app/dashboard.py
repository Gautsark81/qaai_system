import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_app.state import get_engine
from streamlit_app.widgets import draw_sidebar, plot_signal_chart, filter_signals

# Setup
st.set_page_config(page_title="📊 QAAI Signal Dashboard", layout="wide", page_icon="📈")
st.title("🚀 QAAI Trading Dashboard")

# Load engine and symbols
db = get_engine().db
try:
    latest_signals = pd.read_csv("data/signals/latest_signals.csv")
    symbols_available = sorted(latest_signals["symbol"].unique())
except Exception as e:
    st.error("⚠️ Failed to load signals: {}".format(e))
    symbols_available = db.fetch_watchlist() or []

if not symbols_available:
    st.warning("⚠️ No symbols available. Please run the signal engine.")
    st.stop()

# Sidebar controls
symbols, mode, visualize, confidence_threshold, timeframe = draw_sidebar(
    symbols_available
)
engine = get_engine()


# Load trade log
def load_trade_log():
    try:
        df = pd.read_csv("logs/trades/trade_log.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", ascending=False, inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load trade log: {e}")
        return pd.DataFrame()


# Core pipeline
with st.spinner("🔍 Running pipeline..."):
    if mode == "Signal Viewer":
        signal_df = engine.run(symbols)

        if not signal_df.empty:
            filtered_df = filter_signals(signal_df, confidence_threshold)
            if filtered_df.empty:
                st.info("ℹ️ No signals matched your criteria. Try adjusting filters.")
                st.stop()

            st.subheader("📡 Filtered Signals")
            st.dataframe(filtered_df, use_container_width=True)
            st.success(f"✅ {len(filtered_df)} signals shown.")

            # Last signal timestamp
            last_signal_time = pd.to_datetime(filtered_df["timestamp"]).max()
            st.caption(f"🕒 Last Signal Timestamp: {last_signal_time}")

            # Candlestick chart with overlays
            st.subheader("📈 Signal Chart")
            if len(symbols) == 1:
                ohlcv_df = engine.db.fetch_ohlcv(symbols[0], days=100)
                if not ohlcv_df.empty:
                    plot_signal_chart(ohlcv_df, filtered_df, symbols[0])
                else:
                    st.warning("⚠️ No OHLCV data available for this symbol.")
            else:
                st.info("📌 Select one symbol for chart view.")

            # Download
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV", csv, f"{symbols[0]}_signals.csv", "text/csv"
            )
        else:
            st.warning("⚠️ No signals generated.")

    elif mode == "Audit Dashboard":
        trade_df = load_trade_log()
        if trade_df.empty:
            st.warning("⚠️ No trade data available.")
            st.stop()

        # Filters
        with st.sidebar:
            selected_symbols = st.multiselect(
                "Filter by Symbol", trade_df["symbol"].unique()
            )
            selected_status = st.multiselect(
                "Filter by Status", trade_df["status"].unique()
            )
            selected_notes = st.text_input("Search Note Keywords")

        filtered_trades = trade_df.copy()
        if selected_symbols:
            filtered_trades = filtered_trades[
                filtered_trades["symbol"].isin(selected_symbols)
            ]
        if selected_status:
            filtered_trades = filtered_trades[
                filtered_trades["status"].isin(selected_status)
            ]
        if selected_notes:
            filtered_trades = filtered_trades[
                filtered_trades["note"].str.contains(
                    selected_notes, case=False, na=False
                )
            ]

        st.subheader("📋 Trade Audit Log")
        st.dataframe(filtered_trades, use_container_width=True)

        # Summary stats
        win_trades = filtered_trades[filtered_trades["pnl"] > 0]
        total = len(filtered_trades)
        win_rate = len(win_trades) / total * 100 if total else 0

        st.markdown("### 🧮 Summary Stats")
        st.metric("Total Trades", total)
        st.metric("Win Rate", f"{win_rate:.2f}%")
        st.metric("Total PnL", f"₹{filtered_trades['pnl'].sum():.2f}")

        # Charts
        st.markdown("### 📈 PnL Over Time")
        pnl_chart = px.line(
            filtered_trades.sort_values("timestamp"),
            x="timestamp",
            y="pnl",
            color="symbol",
        )
        st.plotly_chart(pnl_chart, use_container_width=True)

        st.markdown("### 🟩 Win/Loss Distribution")
        filtered_trades["Result"] = filtered_trades["pnl"].apply(
            lambda x: "Win" if x > 0 else "Loss"
        )
        win_loss_chart = px.histogram(
            filtered_trades, x="Result", color="Result", barmode="group"
        )
        st.plotly_chart(win_loss_chart, use_container_width=True)

        # Export
        st.download_button(
            "📥 Download Filtered Trade Log",
            filtered_trades.to_csv(index=False),
            "filtered_trade_log.csv",
        )

    else:  # Backtest Mode
        results = engine.backtest_signals(symbols, visualize=visualize)
        if results:
            for symbol, result in results.items():
                st.subheader(f"📊 Backtest Results: {symbol}")
                st.markdown("### 📌 Metrics")
                st.json(result["metrics"])
                st.markdown("### 📋 Recent Signals")
                st.dataframe(result["signals"].tail(10), use_container_width=True)
                st.markdown("### 💹 Trade Log")
                st.dataframe(result["trades"], use_container_width=True)

                if visualize:
                    st.markdown("### 📈 Equity Curve Coming Soon")
        else:
            st.warning("⚠️ No backtest results available.")
