import streamlit as st
from modules.operator_dashboard.runtime import get_runtime_snapshot


def render_overview_page():
    st.title("🧠 QAAI Institutional Control Center")

    state = get_runtime_snapshot()

    st.caption("Stability → Governance → Adaptivity → Intelligence → Scale")

    # -----------------------------
    # Top Control Metrics
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    live = (state.explainability or {}).get("live_proof", {})

    col1.metric(
        "Strategies",
        len(state.strategies or []),
    )

    col2.metric(
        "Active Alerts",
        len(state.alerts or []),
    )

    col3.metric(
        "Live Integrity",
        live.get("chain_integrity_score", 1.0),
    )

    col4.metric(
        "Capital Allocated %",
        sum(
            getattr(s, "capital_allocated_pct", 0) or 0
            for s in state.strategies or []
        ),
    )

    st.divider()

    # -----------------------------
    # Live Integrity Banner
    # -----------------------------
    if live.get("chain_integrity_score", 1.0) < 1.0:
        st.error("🚨 Live proof chain integrity compromised")
    elif live.get("proof_gap_detected"):
        st.warning("⚠️ Live proof inactivity detected")
    else:
        st.success("✅ Live integrity healthy")

    st.divider()

    st.subheader("System Overview")
    st.json(state.system)

    st.subheader("Governance & Oversight")
    st.json(state.oversight_events)