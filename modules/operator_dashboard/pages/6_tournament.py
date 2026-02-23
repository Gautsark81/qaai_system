import streamlit as st
import pandas as pd
from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(page_title="Tournament", layout="wide")

state = DashboardStateAssembler().assemble()

st.title("🏆 Tournament Outcomes")

df = pd.DataFrame([
    {
        "Strategy": s.strategy_id,
        "Stage": s.lifecycle_stage,
        "Last Gate": s.last_gate,
        "Reason": s.last_gate_reason,
    }
    for s in state.strategies
])

st.dataframe(df, use_container_width=True)
