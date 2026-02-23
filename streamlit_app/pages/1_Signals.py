# streamlit_app/pages/1_Signals.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import env_config as cfg
from infra.pnl_calculator import PnLCalculator
from infra.logging_utils import get_logger
from streamlit_app.utils.broker_health import render_broker_health


logger = get_logger("streamlit_signals")

st.set_page_config(page_title="📡 Signal Monitor", layout="wide")
st.title("📡 Signal Monitor & Performance Analytics")

# Sidebar broker health status
render_broker_health()

# === Load Signals ===
@st.cache_data(show_spinner=False)
def load_signals():
    try:
        df = pd.read_csv(cfg.SIGNALS_PATH, parse_dates=["timestamp"])
        df.sort_values("timestamp", inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load signals from {cfg.SIGNALS_PATH}: {e}")
        return pd.DataFrame()


signals_df = load_signals()

if signals_df.empty:
    st.warning("No signals available. Please run the signal engine.")
    st.stop()

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Signals")
symbols = signals_df["symbol"].unique().tolist()
selected_symbols = st.sidebar.multiselect("Select Symbols", symbols, default=symbols)

confidence_range = st.sidebar.slider(
    "Confidence Threshold", 0.0, 1.0, (0.6, 1.0), 0.01
)
signal_type = st.sidebar.radio("Signal Type", ["All", "BUY", "SELL"], index=0)

# === Apply Filters ===
filtered_df = signals_df[
    signals_df["symbol"].isin(selected_symbols)
    & signals_df["confidence"].between(*confidence_range)
]

if signal_type != "All":
    filtered_df = filtered_df[filtered_df["signal"] == signal_type]

# === Display ===
st.subheader(f"Filtered Signals — {len(filtered_df)} Rows")
st.dataframe(filtered_df, use_container_width=True)

# === Performance Analytics (PnLCalculator) ===
if not filtered_df.empty:
    st.markdown("## 📊 Signal Analytics")

    # Convert signals into trade-like dicts for PnLCalculator
    trades = []
    for _, row in filtered_df.iterrows():
        trades.append(
            {
                "symbol": row.get("symbol"),
                "side": row.get("signal", "BUY"),
                "quantity": int(row.get("quantity_hint", 1)),
                "entry_price": float(row.get("price", 100.0)),
                "exit_price": None,
                "status": "open",
                "strategy_id": row.get("strategy_id", "signals_v1"),
                "timestamp": row.get("timestamp"),
            }
        )

    pnl_calc = PnLCalculator(account_equity=1_000_000.0)
    pnl_df = pnl_calc.compute_portfolio_pnl(trades, to_dataframe=True)
    summary = pnl_calc.summarize_portfolio(trades)

    # Portfolio Summary
    st.markdown("### 📌 Portfolio Summary (Filtered Signals)")
    st.json(summary)

    # Equity Curve
    st.markdown("### 📈 Cumulative PnL (Equity Curve)")
    pnl_df["cumulative_pnl"] = pnl_df["total_pnl"].cumsum()
    fig, ax = plt.subplots()
    ax.plot(filtered_df["timestamp"], pnl_df["cumulative_pnl"], marker="o")
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative PnL")
    ax.set_title("Equity Curve from Filtered Signals")
    st.pyplot(fig)

    # Signal Confidence Histogram
    st.markdown("### 📊 Signal Confidence Distribution")
    fig, ax = plt.subplots()
    ax.hist(filtered_df["confidence"], bins=20, edgecolor="black")
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Frequency")
    ax.set_title("Signal Confidence Histogram")
    st.pyplot(fig)

    # Timeline of Signals
    st.markdown("### ⏳ Signal Timeline")
    fig, ax = plt.subplots()
    for sig_type, group in filtered_df.groupby("signal"):
        ax.scatter(group["timestamp"], group["confidence"], label=sig_type, alpha=0.7)
    ax.set_xlabel("Time")
    ax.set_ylabel("Confidence")
    ax.legend()
    ax.set_title("Signals Over Time")
    st.pyplot(fig)

    # Download Option
 export_df = pnl_df.copy()
if "timestamp" in export_df.columns:
    export_df["timestamp"] = (
        pd.to_datetime(export_df["timestamp"], errors="coerce")
        .dt.tz_convert("Asia/Kolkata")
        .dt.tz_localize(None)
    )

csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download CSV",
    csv,
    "filtered_signals_pnl.csv",
    "text/csv",
)
