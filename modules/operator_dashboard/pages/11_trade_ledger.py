import streamlit as st
import pandas as pd
from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(page_title="Trade Ledger", layout="wide")

state = DashboardStateAssembler().assemble()

st.title("📒 Trade Ledger")
st.caption("Backtest · Paper · Live — unified view")

if not state.trades:
    st.info("No trades recorded.")
    st.stop()

df = pd.DataFrame([t.__dict__ for t in state.trades])
st.dataframe(df, use_container_width=True)
