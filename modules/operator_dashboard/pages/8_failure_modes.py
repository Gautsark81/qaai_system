import streamlit as st
import pandas as pd
from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(page_title="Failure Modes", layout="wide")

state = DashboardStateAssembler().assemble()

st.title("🚨 Failure Modes")

failures = [
    s.__dict__
    for s in state.strategies
    if s.status != "allowed" or s.kill_switch_active
]

if not failures:
    st.success("No failures detected.")
else:
    st.dataframe(pd.DataFrame(failures), use_container_width=True)
