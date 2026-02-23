import streamlit as st
from dashboard.view_models import ScreeningVM


def render(data: ScreeningVM) -> None:
    st.subheader("Screening Summary")

    if not data.available:
        st.info("No screening data available.")
        return

    st.write(f"Screening Engine: {data.type}")
