import streamlit as st
from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(page_title="Symbols", layout="wide")

state = DashboardStateAssembler().assemble()

st.title("📈 Symbol Coverage")

active = [s.strategy_id for s in state.strategies if s.status == "allowed"]

st.write("Active strategies:")
st.write(active)
