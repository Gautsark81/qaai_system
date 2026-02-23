import streamlit as st
from dashboard.view_models import MetaAlphaVM


def render(data: MetaAlphaVM) -> None:
    st.subheader("Meta-Alpha Allocation")

    if not data.enabled:
        st.info("Meta-alpha is not active.")
        return

    st.metric("Total Allocated", data.total_allocated)

    if not data.allocations:
        st.info("No allocations present.")
        return

    st.table(data.allocations)
