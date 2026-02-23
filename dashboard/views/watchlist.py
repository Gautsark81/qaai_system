import streamlit as st
from dashboard.view_models import WatchlistVM


def render(data: WatchlistVM) -> None:
    st.subheader("Watchlist")

    if not data.available:
        st.info("Watchlist is empty.")
        return

    st.metric("Symbols", data.count)
    st.caption(f"Type: {data.type}")
