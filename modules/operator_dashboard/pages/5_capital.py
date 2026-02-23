import streamlit as st
from modules.operator_dashboard.runtime import get_runtime_snapshot


def render_capital_page():
    st.title("💰 Capital Governance")

    state = get_runtime_snapshot()

    total_alloc = sum(
        getattr(s, "capital_allocated_pct", 0) or 0
        for s in state.strategies or []
    )

    st.metric("Total Allocated %", total_alloc)

    if total_alloc > 100:
        st.error("Capital allocation exceeds 100%")

    st.divider()
    st.subheader("Capital Snapshot")
    st.json(state.capital)