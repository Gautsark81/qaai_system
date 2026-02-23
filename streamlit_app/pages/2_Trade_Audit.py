# streamlit_app/pages/2_Trade_Audit.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd

from streamlit_app.utils.broker_health import render_broker_health

# Paths to trade logs
CSV_LOG_PATH = "logs/trades/trade_log.csv"
JSONL_LOG_PATH = "logs/trades/trade_log.jsonl"

st.set_page_config(page_title="📊 Trade Audit Dashboard", layout="wide")
st.title("📊 Trade Audit Dashboard")

# Sidebar broker health status
render_broker_health()


# ---------------- Broker Health ----------------
@st.cache_resource
def get_broker():
    try:
        return BrokerAdapter()
    except Exception:
        return None


def broker_health_status():
    broker = get_broker()
    if not broker:
        return "⚠️ Broker adapter not available"
    try:
        ok, msg = broker.ping_broker()
        if ok:
            return f"✅ Broker healthy ({msg})"
        return f"❌ Broker issue: {msg}"
    except Exception as e:
        return f"❌ Broker ping failed: {e}"


st.sidebar.markdown("### 🩺 Broker Health")
st.sidebar.info(broker_health_status())


# ---------------- Load Trade Data ----------------
def load_trade_data():
    if os.path.exists(CSV_LOG_PATH):
        df = pd.read_csv(CSV_LOG_PATH)
    elif os.path.exists(JSONL_LOG_PATH):
        with open(JSONL_LOG_PATH, "r") as f:
            records = [json.loads(line) for line in f]
        df = pd.DataFrame(records)
    else:
        st.warning("No trade logs found.")
        return pd.DataFrame()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.sort_values("timestamp", ascending=False, inplace=True)
    return df


# ---------------- Filter Sidebar ----------------
def trade_filter_sidebar(df):
    st.sidebar.header("🔍 Filters")

    symbols = df["symbol"].dropna().unique().tolist()
    strategies = df["strategy_id"].dropna().unique().tolist()
    statuses = df["status"].dropna().unique().tolist()

    selected_symbols = st.sidebar.multiselect("Symbol", symbols, default=symbols)
    selected_strategies = st.sidebar.multiselect(
        "Strategy ID", strategies, default=strategies
    )
    selected_status = st.sidebar.multiselect("Status", statuses, default=statuses)

    df = df[df["symbol"].isin(selected_symbols)]
    df = df[df["strategy_id"].isin(selected_strategies)]
    df = df[df["status"].isin(selected_status)]

    return df


# ---------------- Summary Stats ----------------
def show_summary_metrics(df):
    total_trades = len(df)
    wins = df[df["pnl"] > 0].shape[0]
    losses = df[df["pnl"] < 0].shape[0]
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    avg_pnl = df["pnl"].mean() if "pnl" in df.columns else 0
    max_drawdown = df["pnl"].min() if "pnl" in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.2f}%")
    col3.metric("Avg PnL", f"₹{avg_pnl:.2f}")
    col4.metric("Max Drawdown", f"₹{max_drawdown:.2f}")


# ---------------- Export Helpers ----------------
@st.cache_data(show_spinner=False)
def convert_df(df):
    export_df = df.copy()
    if "timestamp" in export_df.columns:
        export_df["timestamp"] = (
            pd.to_datetime(export_df["timestamp"], errors="coerce")
            .dt.tz_convert("Asia/Kolkata")
            .dt.tz_localize(None)
        )
    return export_df.to_csv(index=False).encode("utf-8")


# ---------------- Main App ----------------
trade_df = load_trade_data()

if not trade_df.empty:
    filtered_df = trade_filter_sidebar(trade_df)
    show_summary_metrics(filtered_df)
    show_trade_table(filtered_df)
else:
    st.info("Upload trade log file to begin.")
