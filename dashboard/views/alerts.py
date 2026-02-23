import streamlit as st
from dashboard.view_models import AlertsVM


def render(data: AlertsVM) -> None:
    st.subheader("Alerts")

    if data.count == 0:
        st.success("No active alerts.")
        return

    for alert in data.alerts:
        st.warning(alert)
