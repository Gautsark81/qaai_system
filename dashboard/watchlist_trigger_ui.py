# File: dashboard/watchlist_trigger_ui.py

import streamlit as st
from watchlist.auto_watchlist_builder import AutoWatchlistBuilder

st.set_page_config(page_title="QAAI Watchlist Manager", layout="centered")

st.title("📈 Auto-Adaptive Watchlist Manager")

if st.button("⚡ Run Auto Watchlist Builder Now"):
    builder = AutoWatchlistBuilder()
    builder.update_watchlist()
    st.success("✅ Watchlist updated successfully!")

st.info(
    "This will fetch top 50 high-volume NSE stocks using Dhan API and update the database."
)
