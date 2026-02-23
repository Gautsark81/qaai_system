import streamlit as st

from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(
    page_title="Strategy Detail",
    layout="wide",
)

st.title("📌 Strategy Detail")
st.caption("Deep inspection of a single strategy · Deterministic view")

# -----------------------------
# Load dashboard state
# -----------------------------
state = DashboardStateAssembler().assemble()

# -----------------------------
# Guard: no strategies
# -----------------------------
if not state.strategies:
    st.info("No strategies available to display.")
    st.stop()

# -----------------------------
# Strategy selection
# -----------------------------
strategy_ids = [s.strategy_id for s in state.strategies]

selected_id = st.selectbox(
    "Select Strategy",
    strategy_ids,
)

strategy = next(
    (s for s in state.strategies if s.strategy_id == selected_id),
    None,
)

if strategy is None:
    st.warning("Selected strategy not found.")
    st.stop()

# -----------------------------
# Summary
# -----------------------------
st.subheader("🧾 Strategy Summary")
st.json(strategy.__dict__)

# -----------------------------
# Lifecycle & Governance
# -----------------------------
st.subheader("🧭 Lifecycle & Governance")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Status", strategy.status)

with col2:
    st.metric("Lifecycle Stage", strategy.lifecycle_stage)

with col3:
    st.metric(
        "Approval Status",
        strategy.approval.status if strategy.approval else "N/A",
    )

# -----------------------------
# Safety Signals
# -----------------------------
st.subheader("🛑 Safety Signals")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Kill Switch Active",
        "YES" if strategy.kill_switch_active else "NO",
    )

with c2:
    st.metric(
        "Canary Active",
        "YES" if strategy.canary_active else "NO",
    )

with c3:
    st.metric(
        "Paper SSR",
        f"{strategy.paper_ssr:.2f}" if strategy.paper_ssr is not None else "N/A",
    )
