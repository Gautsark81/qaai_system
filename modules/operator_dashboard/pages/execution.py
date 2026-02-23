import streamlit as st
from modules.operator_dashboard.runtime import get_runtime_snapshot


def render_execution_page():
    st.title("⚙️ Execution Telemetry")

    state = get_runtime_snapshot()

    st.subheader("System Execution Status")
    st.json(state.system)

    st.subheader("Alerts")
    for a in state.alerts or []:
        severity = a.get("severity", "INFO")

        if severity == "CRITICAL":
            st.error(a.get("message"))
        elif severity == "WARNING":
            st.warning(a.get("message"))
        else:
            st.info(a.get("message"))