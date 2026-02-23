# streamlit_app/app.py

import streamlit as st

st.set_page_config(page_title="Quant AI Dashboard", layout="wide", page_icon="📊")

# Optional: Add custom logo or branding
st.sidebar.image("assets/logo.png", width=180)

st.sidebar.title("Navigation")
st.sidebar.page_link("pages/1_Signals.py", label="🔍 Signal Monitor")
st.sidebar.page_link("pages/2_Backtest.py", label="⏲️ Backtester")
st.sidebar.page_link("pages/3_Performance.py", label="🏋️ Performance")
st.sidebar.page_link("pages/4_Watchlist.py", label="🔍 Watchlist")

st.title("🚀 Quant AI - Advanced Trading Dashboard")
st.markdown(
    """
Welcome to your full-stack Streamlit dashboard for signal generation, backtesting, performance analytics, and watchlist management.
"""
)

st.info("Use the sidebar to navigate between modules.")
