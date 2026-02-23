import streamlit as st
from dashboard.view_models import OverviewVM


def render(data: OverviewVM) -> None:
    st.subheader("System Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Alerts", data.alert_count)
    col2.metric(
        "Strategies Available",
        "Yes" if data.has_strategies else "No",
    )
    col3.metric(
        "Watchlist Available",
        "Yes" if data.has_watchlist else "No",
    )

    st.caption(f"Snapshot timestamp: {data.timestamp}")
