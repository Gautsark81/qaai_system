"""
Policy Feedback Panel (READ-ONLY)

Surfaces:
- Promotion precision / recall
- Approval quality score
- Human-readable policy recommendations (Phase-17)

🚫 No policy mutation
🚫 No threshold sliders
🚫 No auto-apply
"""

from typing import List
import streamlit as st

from modules.operator_dashboard.data_contracts import PolicyFeedbackDTO


def render_policy_feedback_panel(
    feedback: PolicyFeedbackDTO,
):
    st.subheader("🧠 Governance Policy Feedback (Read-Only)")

    # --- Summary metrics ---
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Promotion Precision",
        f"{feedback.promotion_precision:.2f}",
        help="How often promoted strategies succeeded",
    )

    col2.metric(
        "Promotion Recall",
        f"{feedback.promotion_recall:.2f}",
        help="How many successful strategies were promoted",
    )

    col3.metric(
        "Approval Quality Score",
        f"{feedback.approval_score:.2f}",
        help="Historical success rate of approvals",
    )

    st.divider()

    # --- Recommendations ---
    st.markdown("### 📌 Recommendations (Offline Review Only)")

    if not feedback.recommendations:
        st.success("No governance issues detected. No changes recommended.")
    else:
        for idx, rec in enumerate(feedback.recommendations, start=1):
            with st.container(border=True):
                st.markdown(f"**#{idx} Recommendation**")
                st.markdown(rec)

    st.info(
        "🔒 These recommendations are advisory only.\n\n"
        "Policy changes must be reviewed, versioned, and applied offline.\n"
        "This dashboard cannot modify live rules."
    )
