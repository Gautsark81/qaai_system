import sys
import os
import streamlit as st
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.signal_engine import SignalEngine, persist_model

st.set_page_config(page_title="Signal Dashboard", layout="wide")
st.title("📊 Trading Signal Dashboard")

# === Sidebar ===
st.sidebar.header("Signal Configuration")
symbols_input = st.sidebar.text_input(
    "Enter symbols (comma-separated)", "RELIANCE,TCS,INFY"
)
symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
run_button = st.sidebar.button("🚀 Run Signal Engine")

# === Run Signal Engine ===
if run_button and symbols:
    st.info("Running signal engine. Please wait...")
    engine = SignalEngine()
    signal_df = engine.run(symbols)
    persist_model()

    if not signal_df.empty:
        st.success(f"✅ Generated {len(signal_df)} signals")

        # === Portfolio Overview ===
        st.subheader("📦 Signal Summary")
        st.dataframe(signal_df.tail(20))

        # === Signal Distribution ===
        st.subheader("📈 Signal Distribution")
        fig = px.histogram(signal_df, x="signal", color="symbol", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        # === Confidence over Time ===
        st.subheader("📉 Confidence Over Time")
        fig2 = px.line(signal_df, x="timestamp", y="confidence", color="symbol")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ No signals generated. Try other symbols or check data source.")

elif not run_button:
    st.info("👈 Enter symbols and click 'Run Signal Engine'")
