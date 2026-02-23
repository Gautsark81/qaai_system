import streamlit as st
from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(page_title="Alerts", layout="wide")

state = DashboardStateAssembler().assemble()

st.title("🚨 Alerts")

if not state.alerts:
    st.success("No active alerts.")
else:
    for a in state.alerts:
        st.error(f"[{a.alert_type}] {a.message}")
