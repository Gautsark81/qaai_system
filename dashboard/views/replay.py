import streamlit as st
from typing import Iterable

from dashboard.view_models import (
    ReplayResultVM,
    ReplayDiffReportVM,
)


def render(
    results: Iterable[ReplayResultVM],
    diffs: Iterable[ReplayDiffReportVM],
) -> None:
    st.subheader("Execution Replay (Read-Only)")

    results = list(results)
    diffs = list(diffs)

    if not results and not diffs:
        st.info("No replay data available.")
        return

    if results:
        st.markdown("### Replay Results")
        for r in results:
            st.write(
                f"Replay `{r.replay_id}` · "
                f"Completed: {r.completed_at}"
            )
            if r.invariant_violations:
                st.warning(
                    f"Invariant violations: "
                    f"{', '.join(r.invariant_violations)}"
                )
            else:
                st.success("All invariants satisfied")

    if diffs:
        st.markdown("### Replay vs Live Differences")
        for d in diffs:
            st.write(
                f"Replay `{d.replay_id}` · "
                f"Compared at {d.compared_at}"
            )
            if not d.diffs:
                st.success("No differences detected")
            else:
                for item in d.diffs:
                    st.error(f"[{item.code}] {item.message}")
