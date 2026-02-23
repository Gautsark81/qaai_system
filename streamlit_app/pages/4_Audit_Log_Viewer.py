# streamlit_app/pages/4_Audit_Log_Viewer.py
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

# --- Ensure project root is in sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Local imports ---
from streamlit_app.utils.broker_health import render_broker_health
from db.db_utils import fetch_recent_runs, fallback_load_audit_logs
from infra.logging_utils import get_logger

logger = get_logger("streamlit_audit_viewer")

# Sidebar broker health status
render_broker_health()

st.set_page_config(page_title="📋 Audit Log Viewer", layout="wide")
st.title("📋 Audit Log Viewer & Compliance Dashboard")
st.caption(
    "Review pipeline runs, reconcile orders, and detect anomalies from audit logs."
)

# === Load Audit Logs (DB first, fallback JSONL) ===
try:
    df = fetch_recent_runs(limit=50)
    if df.empty:
        raise ValueError("No DB records")
    logs = df.to_dict("records")
    st.success("✅ Loaded from Postgres")
except Exception as e:
    st.warning(f"⚠️ DB not available ({e}), falling back to JSONL.")
    logs = fallback_load_audit_logs()

if not logs:
    st.warning("⚠️ No audit logs found. Run main_orchestrator.py to generate logs.")
    st.stop()

# === Sidebar Filters ===
st.sidebar.header("Filters")

modes = sorted({log.get("mode", "unknown") for log in logs})
mode_filter = st.sidebar.multiselect("Mode", modes, default=modes)

symbols = sorted(
    {
        s.get("symbol")
        for log in logs
        for s in log.get("signals", [])
        if isinstance(log.get("signals"), list) and s.get("symbol")
    }
)
symbol_filter = st.sidebar.multiselect("Symbols", symbols)


# === Helper: Build equity curve ===
def build_equity_curve(logs, mode_filter, symbol_filter):
    records = []
    for log in logs:
        if mode_filter and log.get("mode") not in mode_filter:
            continue
        for order in log.get("orders", []):
            if symbol_filter and order.get("symbol") not in symbol_filter:
                continue
            records.append(
                {
                    "timestamp": log.get("run_timestamp")
                    or log.get("meta", {}).get("timestamp"),
                    "symbol": order.get("symbol"),
                    "side": order.get("side"),
                    "price": order.get("price"),
                    "qty": order.get("quantity", 1),
                }
            )
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["pnl_step"] = df.apply(
        lambda r: (
            r["qty"] * r["price"]
            if str(r["side"]).upper() in ("SELL", "SHORT")
            else -r["qty"] * r["price"]
        ),
        axis=1,
    )
    df["cumulative_pnl"] = df["pnl_step"].cumsum()
    return df


# === Equity curve ===
st.subheader("📈 Portfolio Equity Curve (from executed orders)")
equity_df = build_equity_curve(logs, mode_filter, symbol_filter)

if not equity_df.empty:
    fig, ax = plt.subplots()
    ax.plot(equity_df["timestamp"], equity_df["cumulative_pnl"], marker="o")
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative PnL (Simulated)")
    ax.set_title("Equity Curve Across Runs")
    st.pyplot(fig)
else:
    st.info("No orders found matching filters for equity curve.")

# === Anomaly detection ===
st.subheader("⚠️ Anomaly Detection")
anomalies = []
for log in logs:
    for order in log.get("orders", []):
        if order.get("price", 0) <= 0:
            anomalies.append({"issue": "Invalid price", "order": order})
        if order.get("quantity", 0) <= 0:
            anomalies.append({"issue": "Invalid quantity", "order": order})

if anomalies:
    st.error(f"Found {len(anomalies)} anomalies in logs.")
    st.json(anomalies[:10])
else:
    st.success("No anomalies detected.")

# === Individual run explorer ===
st.subheader("🕒 Pipeline Run Explorer")
for log in logs:
    meta = log.get("meta", {})
    if mode_filter and meta.get("mode") not in mode_filter:
        continue
    if symbol_filter:
        sig_syms = {s.get("symbol") for s in log.get("signals", [])}
        if not set(symbol_filter) & sig_syms:
            continue
    with st.expander(
        f"{meta.get('timestamp', 'unknown')} | Mode={meta.get('mode')} | TopK={meta.get('top_k')}"
    ):
        st.json(meta)

        st.markdown("### 📊 Watchlist")
        watchlist = pd.DataFrame(log.get("watchlist", []))
        (
            st.dataframe(watchlist)
            if not watchlist.empty
            else st.info("No watchlist data.")
        )

        st.markdown("### 🔍 Signals")
        signals = pd.DataFrame(log.get("signals", []))
        st.dataframe(signals) if not signals.empty else st.info("No signals generated.")

        st.markdown("### 📈 Orders")
        orders = pd.DataFrame(log.get("orders", []))
        st.dataframe(orders) if not orders.empty else st.info("No orders placed.")

# === XLSX export ===
st.subheader("📥 Export Audit Report")
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    if not equity_df.empty:
        df_to_save = equity_df.copy()
        if pd.api.types.is_datetime64_any_dtype(df_to_save["timestamp"]):
            df_to_save["timestamp"] = (
                pd.to_datetime(df_to_save["timestamp"], errors="coerce")
                .dt.tz_convert("Asia/Kolkata")  # convert to IST
                .dt.tz_localize(None)  # make tz-naive for Excel
            )
        df_to_save.to_excel(writer, index=False, sheet_name="Equity_Curve")

    for i, log in enumerate(logs[:10]):
        orders_df = pd.DataFrame(log.get("orders", []))
        if not orders_df.empty and "timestamp" in orders_df.columns:
            orders_df["timestamp"] = (
                pd.to_datetime(orders_df["timestamp"], errors="coerce")
                .dt.tz_convert("Asia/Kolkata")  # convert to IST
                .dt.tz_localize(None)  # make tz-naive for Excel
            )
        orders_df.to_excel(writer, index=False, sheet_name=f"Run_{i}_Orders")

st.download_button(
    label="📥 Download Audit Report XLSX",
    data=output.getvalue(),
    file_name="audit_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
