"""
Kill Timeline View (READ-ONLY)

Visualizes:
- Kill events in reverse chronological order
- Kill reasons and supporting details
- Time context for operator trust

🚫 No revive
🚫 No override
🚫 No mutation
"""

from typing import List
from datetime import datetime
import streamlit as st

from modules.operator_dashboard.data_contracts import KillEventDTO


def render_kill_timeline_view(
    kills: List[KillEventDTO],
    now: datetime,
):
    st.subheader("🧨 Kill & Rollback Timeline")

    if not kills:
        st.info("No kill events recorded.")
        return

    # Newest first
    kills_sorted = sorted(kills, key=lambda k: k.killed_at, reverse=True)

    for k in kills_sorted:
        hours_ago = (now - k.killed_at).total_seconds() / 3600

        if hours_ago < 1:
            time_label = f"{hours_ago * 60:.0f} min ago"
            color = "red"
        elif hours_ago < 24:
            time_label = f"{hours_ago:.1f} h ago"
            color = "orange"
        else:
            time_label = f"{hours_ago/24:.1f} days ago"
            color = "gray"

        with st.container(border=True):
            st.markdown(f"### `{k.strategy_id}`")
            st.markdown(f"**Killed:** :{color}[{time_label}]")
            st.markdown(f"**Reason:** `{k.reason}`")
            st.markdown(f"**Details:** {k.details}")
            st.markdown(
                f"**Timestamp:** {k.killed_at.isoformat()}"
            )

    st.info(
        "🔒 Kill actions are final and cannot be reversed from the dashboard.\n\n"
        "Review governance and policy feedback for future improvements."
    )
