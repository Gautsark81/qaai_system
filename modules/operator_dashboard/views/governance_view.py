"""
Governance Approval Timeline View (READ-ONLY)

This view visualizes:
- Approval status
- Approver identity
- TTL / expiry
- Capital context (if provided upstream)

🚫 No approval actions
🚫 No mutation
🚫 No execution
"""

from datetime import datetime
from typing import List
import streamlit as st

from modules.operator_dashboard.data_contracts import ApprovalStatusDTO


def render_governance_approval_timeline(
    approvals: List[ApprovalStatusDTO],
    now: datetime,
):
    st.subheader("🛡️ Governance Approval Timeline")

    if not approvals:
        st.info("No approval records available.")
        return

    for a in approvals:
        if not a.approved:
            status = "❌ NOT APPROVED"
            color = "red"
        elif a.expires_at and a.expires_at < now:
            status = "⏱️ EXPIRED"
            color = "red"
        else:
            remaining = (
                a.expires_at - now
            ).total_seconds() / 3600 if a.expires_at else None

            if remaining is not None and remaining < 6:
                status = f"🟠 APPROVED (expires in {remaining:.1f}h)"
                color = "orange"
            else:
                status = "🟢 APPROVED"
                color = "green"

        with st.container(border=True):
            st.markdown(f"### Strategy: `{a.strategy_id}`")
            st.markdown(f"**Status:** :{color}[{status}]")

            if a.approver:
                st.markdown(f"**Approver:** {a.approver}")

            if a.expires_at:
                st.markdown(
                    f"**Expires at:** {a.expires_at.isoformat()}"
                )

            if a.reason:
                st.markdown(f"**Reason:** {a.reason}")

    st.info(
        "🔒 Approvals cannot be made from this dashboard.\n\n"
        "Use the CLI approval command from Phase-13.5."
    )
