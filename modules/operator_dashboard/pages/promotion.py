import streamlit as st
from modules.operator_dashboard.runtime import get_runtime_snapshot


def render_promotion_page():
    st.title("🏆 Promotion & Lifecycle")

    state = get_runtime_snapshot()

    for s in state.strategies or []:
        st.subheader(s.strategy_id)

        col1, col2 = st.columns(2)

        col1.metric("Lifecycle Stage", getattr(s, "lifecycle_stage", None))
        col2.metric("SSR", getattr(s, "ssr", None))

        st.divider()