"""
Live Admission Status Board (READ-ONLY)

Visualizes:
- Which strategies are currently admitted to live trading
- Admission expiry countdown
- Capital allocation
- Token session awareness

🚫 No re-admit
🚫 No revoke
🚫 No execution
"""

from datetime import datetime
from typing import List
import streamlit as st

from modules.operator_dashboard.data_contracts import LiveAdmissionDTO


def render_live_admission_status_board(
    admissions: List[LiveAdmissionDTO],
    now: datetime,
):
    st.subheader("🚦 Live Admission Status Board")

    if not admissions:
        st.info("No strategies are currently admitted to live trading.")
        return

    cols = st.columns(3)

    for idx, a in enumerate(admissions):
        with cols[idx % 3]:
            remaining_hours = (
                a.expires_at - now
            ).total_seconds() / 3600

            if remaining_hours <= 0:
                status = "⛔ EXPIRED"
                color = "red"
            elif remaining_hours < 2:
                status = f"🟠 EXPIRING ({remaining_hours:.1f}h)"
                color = "orange"
            else:
                status = f"🟢 ACTIVE ({remaining_hours:.1f}h)"
                color = "green"

            with st.container(border=True):
                st.markdown(f"### `{a.strategy_id}`")
                st.markdown(f"**Status:** :{color}[{status}]")
                st.markdown(f"**Capital:** ₹{a.capital:,.0f}")
                st.markdown(
                    f"**Admitted at:** {a.admitted_at.isoformat()}"
                )
                st.markdown(
                    f"**Expires at:** {a.expires_at.isoformat()}"
                )
                st.markdown(
                    f"**Token session:** `{a.token_session_id}`"
                )

    st.info(
        "🔒 Live admission cannot be modified from this dashboard.\n\n"
        "Re-admission requires valid approval + token via Phase-14."
    )
