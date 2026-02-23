import streamlit as st
from modules.operator_dashboard.runtime import get_runtime_snapshot


def render_failure_page():
    st.title("🚨 System Risk & Failure Modes")

    state = get_runtime_snapshot()

    if not state.alerts:
        st.success("No active failures.")
        return

    for a in state.alerts:
        severity = a.get("severity", "INFO")

        if severity == "CRITICAL":
            st.error(f"[{a.get('type')}] {a.get('message')}")
        elif severity == "WARNING":
            st.warning(f"[{a.get('type')}] {a.get('message')}")
        else:
            st.info(f"[{a.get('type')}] {a.get('message')}")