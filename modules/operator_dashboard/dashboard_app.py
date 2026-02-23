# ---------------------------------------------
# PYTHONPATH BOOTSTRAP (REQUIRED FOR STREAMLIT)
# ---------------------------------------------
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "modules"

if str(MODULES) not in sys.path:
    sys.path.insert(0, str(MODULES))

# ---------------------------------------------
# STREAMLIT IMPORT (AFTER PATH FIX)
# ---------------------------------------------
import streamlit as st

from modules.operator_dashboard.state_assembler import DashboardStateAssembler
from modules.operator_dashboard.pages.live_proof import render_live_proof_page

# ---------------------------------------------
# STREAMLIT CONFIG
# ---------------------------------------------
st.set_page_config(
    page_title="QAAI Operator Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("QAAI • Operator Dashboard")

st.markdown(
    """
    **Stability first → Adaptivity second → Intelligence last**
    """
)

# ---------------------------------------------
# Navigation
# ---------------------------------------------
page = st.sidebar.selectbox(
    "Navigation",
    [
        "Overview",
        "Live Proof Integrity",
    ],
)

if page == "Live Proof Integrity":
    render_live_proof_page()
    st.stop()

# ---------------------------------------------
# Default Overview Page
# ---------------------------------------------
snapshot = DashboardStateAssembler().assemble_full()

st.subheader("System Overview")
st.json(snapshot.system)

st.subheader("Capital")
st.json(snapshot.capital)

st.subheader("Strategies")
st.json(snapshot.strategies)

st.subheader("Alerts")
st.json(snapshot.alerts)