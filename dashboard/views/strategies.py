import streamlit as st
from dashboard.view_models import StrategiesVM


def render(data: StrategiesVM) -> None:
    st.subheader("Strategy Intelligence")

    if not data.available:
        st.info("No strategy intelligence available.")
        return

    st.write(f"Strategy Container: {data.type}")
