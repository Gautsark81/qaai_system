"""
Live Proof Panel (UI-ONLY)

Strict rules:
- No core imports
- No state mutation
- Read-only snapshot consumption
"""

from typing import Any, Dict, Optional
import streamlit as st


def render_live_proof_panel(snapshot: Any) -> None:
    """
    Render Live Execution Proof panel.

    Safe:
    - Never mutates snapshot
    - Never imports core
    - Gracefully handles missing proof
    """

    explainability: Optional[Dict] = getattr(snapshot, "explainability", None)

    st.markdown("## 🔐 Live Execution Proof")

    if not explainability or "live_proof" not in explainability:
        st.info("Live proof data not available.")
        return

    proof = explainability["live_proof"]

    if not isinstance(proof, dict):
        st.warning("Live proof format invalid.")
        return

    total = proof.get("total_artifacts", 0)
    last_hash = proof.get("last_hash")
    authority_valid = proof.get("authority_all_valid", True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Artifacts Recorded", total)

    col2.metric(
        "Authority Validated",
        "YES" if authority_valid else "NO",
    )

    col3.metric(
        "Last Chain Hash",
        (last_hash[:12] if last_hash else "—"),
    )

    if not authority_valid:
        st.error("⚠ Authority validation failure detected.")
    else:
        st.success("All execution authority validations passed.")