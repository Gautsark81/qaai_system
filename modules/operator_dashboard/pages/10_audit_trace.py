import streamlit as st
from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(page_title="Audit Trace", layout="wide")

state = DashboardStateAssembler().assemble()

st.title("🧾 Audit & Decision Trace")
st.caption("Immutable decision trail · No inference")

if not state.audit_events:
    st.info("No audit events recorded.")
    st.stop()

for e in state.audit_events:
    st.markdown(
        f"""
**{e.timestamp}**  
• Strategy: `{e.strategy_id}`  
• Action: `{e.action}`  
• Actor: `{e.actor}`  
• Reason: {e.reason}
"""
    )
