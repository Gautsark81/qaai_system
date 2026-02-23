import streamlit as st
import pandas as pd

from operator_dashboard.state_assembler import DashboardStateAssembler

st.set_page_config(
    page_title="Strategy Comparisons",
    layout="wide",
)

st.title("📊 Strategy Comparisons")
st.caption("Side-by-side performance & risk comparison")

# -----------------------------
# Load dashboard state
# -----------------------------
state = DashboardStateAssembler().assemble()

# -----------------------------
# Guard: no strategies
# -----------------------------
if not state.strategies:
    st.info("No strategies available for comparison.")
    st.stop()

# -----------------------------
# Build dataframe
# -----------------------------
df = pd.DataFrame(
    [
        {
            "strategy_id": s.strategy_id,
            "status": s.status,
            "lifecycle_stage": s.lifecycle_stage,
            "paper_ssr": s.paper_ssr,
            "kill_switch_active": s.kill_switch_active,
            "canary_active": s.canary_active,
        }
        for s in state.strategies
    ]
)

if df.empty:
    st.info("No comparable strategy data available.")
    st.stop()

# -----------------------------
# Selection
# -----------------------------
selected_ids = st.multiselect(
    "Select strategies to compare",
    options=df["strategy_id"].tolist(),
    default=df["strategy_id"].head(2).tolist(),
)

if not selected_ids:
    st.warning("Select at least one strategy to compare.")
    st.stop()

comparison_df = df[df["strategy_id"].isin(selected_ids)]

# -----------------------------
# Display comparison table
# -----------------------------
st.subheader("📋 Comparison Table")
st.dataframe(
    comparison_df,
    width="stretch",
)

# -----------------------------
# Simple insights
# -----------------------------
st.subheader("🔍 Observations")

if comparison_df["paper_ssr"].notna().any():
    best = comparison_df.sort_values(
        by="paper_ssr",
        ascending=False,
        na_position="last",
    ).iloc[0]

    st.success(
        f"Best Paper SSR: **{best.strategy_id}** "
        f"({best.paper_ssr:.2f})"
    )
else:
    st.info("No Paper SSR data available for comparison.")
