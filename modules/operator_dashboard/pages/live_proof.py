import streamlit as st
from modules.operator_dashboard.state_assembler import DashboardStateAssembler


def render_live_proof_page():
    st.title("🔐 Live Proof Integrity")

    snapshot = DashboardStateAssembler().assemble_full()
    explainability = snapshot.explainability or {}
    live_proof = explainability.get("live_proof")

    if not live_proof:
        st.warning("Live proof diagnostics unavailable.")
        return

    total = live_proof.get("total_artifacts", 0)
    integrity_score = live_proof.get("chain_integrity_score", 1.0)
    duplicate_detected = live_proof.get("duplicate_hash_detected", False)
    inactivity = live_proof.get("proof_gap_detected", False)

    # --------------------------------------------
    # Integrity Banner
    # --------------------------------------------
    if integrity_score < 1.0 or duplicate_detected:
        st.error("🚨 Live Proof Integrity Failure Detected")
    elif inactivity:
        st.warning("⚠️ No recent live proof artifacts detected")
    else:
        st.success("✅ Live Proof Integrity Healthy")

    # --------------------------------------------
    # Metrics
    # --------------------------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Artifacts", total)
    col2.metric("Integrity Score", integrity_score)
    col3.metric(
        "Unique Hash Ratio",
        live_proof.get("unique_hash_ratio", 1.0),
    )

    st.divider()

    st.subheader("Diagnostic Details")
    st.json(live_proof)