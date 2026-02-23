# streamlit_app/pages/3_Alpha_Intel_Overlays.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import env_config as cfg
from infra.logging_utils import get_logger
from streamlit_app.utils.broker_health import render_broker_health

logger = get_logger("streamlit_alpha_overlays")

# Sidebar broker health status
render_broker_health()

st.set_page_config(page_title="📈 Alpha Intelligence Overlays", layout="wide")
st.title("🧠 Alpha Intelligence Overlays")


@st.cache_data(show_spinner=False)
def load_price_data():
    if os.path.exists(cfg.MARKET_LOG_PATH):
        return pd.read_csv(cfg.MARKET_LOG_PATH, parse_dates=["timestamp"])
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_trade_log():
    if os.path.exists(cfg.TRADE_LOG_PATH):
        return pd.read_csv(cfg.TRADE_LOG_PATH, parse_dates=["timestamp"])
    return pd.DataFrame()


price_df = load_price_data()
trade_df = load_trade_log()

# === Market Regime Timeline ===
if not price_df.empty:
    with st.expander("📊 Market Regime Timeline", expanded=True):
        try:
            from signal.regime_classifier import regime_flags

            flagged = regime_flags(price_df)
        except Exception:
            flagged = price_df.copy()
            flagged["regime"] = "neutral"

        st.line_chart(flagged.set_index("timestamp")["close"])
        st.dataframe(
            flagged[["timestamp", "close", "regime"]].tail(20), use_container_width=True
        )

# === Signal quality and overlays ===
if not trade_df.empty:
    with st.expander("🔥 Signal Quality Dashboard", expanded=True):
        try:
            from screening.quality_control import evaluate_signal_quality

            feedback = evaluate_signal_quality(trade_df)
        except Exception:
            if "symbol" in trade_df.columns and "pnl" in trade_df.columns:
                feedback = (
                    trade_df.groupby("symbol")["pnl"]
                    .mean()
                    .reset_index()
                    .rename(columns={"pnl": "quality_score"})
                )
            else:
                feedback = pd.DataFrame(columns=["symbol", "quality_score"])

        st.dataframe(feedback, use_container_width=True)
        if not feedback.empty:
            st.bar_chart(feedback.set_index("symbol")["quality_score"])

    # === SL/TP Heatmap ===
    with st.expander("🌡️ SL/TP Heatmap by Strategy", expanded=True):
        if {"strategy_id", "exit_reason"}.issubset(trade_df.columns):
            sl_tp_counts = (
                trade_df.groupby(["strategy_id", "exit_reason"])
                .size()
                .unstack(fill_value=0)
            )

            fig, ax = plt.subplots(figsize=(6, len(sl_tp_counts) * 0.5 + 1))
            im = ax.imshow(sl_tp_counts.values, cmap="coolwarm")

            # Show all ticks
            ax.set_xticks(np.arange(len(sl_tp_counts.columns)))
            ax.set_yticks(np.arange(len(sl_tp_counts.index)))
            ax.set_xticklabels(sl_tp_counts.columns)
            ax.set_yticklabels(sl_tp_counts.index)

            # Rotate tick labels
            plt.setp(
                ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
            )

            # Annotate cells
            for i in range(len(sl_tp_counts.index)):
                for j in range(len(sl_tp_counts.columns)):
                    ax.text(
                        j,
                        i,
                        sl_tp_counts.values[i, j],
                        ha="center",
                        va="center",
                        color="black",
                    )

            ax.set_title("SL/TP Heatmap by Strategy")
            st.pyplot(fig)
        else:
            st.warning("SL/TP data or strategy_id column missing in trade log.")

    # === Advanced Intelligence Overlays ===
    with st.expander("🧮 Advanced Intelligence Overlays", expanded=False):
        st.markdown("### 📈 Multi-Layer Intelligence")

        if "strategy_id" in trade_df.columns and "pnl" in trade_df.columns:
            strat_perf = trade_df.groupby("strategy_id")["pnl"].sum().reset_index()
            st.bar_chart(strat_perf.set_index("strategy_id")["pnl"])

        if "atr" in trade_df.columns and "pnl" in trade_df.columns:
            st.markdown("#### ATR vs PnL Correlation")
            fig, ax = plt.subplots()
            for strat, grp in trade_df.groupby("strategy_id"):
                ax.scatter(grp["atr"], grp["pnl"], alpha=0.7, label=strat)
            ax.set_xlabel("ATR")
            ax.set_ylabel("PnL")
            ax.set_title("ATR vs PnL Correlation")
            ax.legend()
            st.pyplot(fig)

        if "confidence" in trade_df.columns:
            st.markdown("#### Confidence vs Trade Outcomes")
            fig, ax = plt.subplots()
            wins = trade_df[trade_df["pnl"] > 0]["confidence"]
            losses = trade_df[trade_df["pnl"] <= 0]["confidence"]
            ax.hist(
                [wins, losses],
                bins=20,
                stacked=True,
                label=["Win", "Loss"],
                alpha=0.7,
            )
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Count")
            ax.legend()
            st.pyplot(fig)

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
