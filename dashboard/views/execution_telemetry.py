import streamlit as st
from dashboard.view_models import ExecutionTelemetryVM


def render(data: ExecutionTelemetryVM) -> None:
    st.subheader("Execution Telemetry")

    st.caption(f"Execution ID: {data.execution_id}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", data.total_orders)
    col2.metric("Filled", data.filled_orders)
    col3.metric("Rejected", data.rejected_orders)
    col4.metric("Cancelled", data.cancelled_orders)

    st.divider()

    if data.invariant_violations:
        st.error("Invariant Violations Detected")
        for v in data.invariant_violations:
            st.warning(f"[{v.code}] {v.message}")
    else:
        st.success("All execution invariants satisfied")

    st.divider()

    if not data.events:
        st.info("No execution events recorded.")
        return

    st.markdown("### Execution Events")
    for e in data.events:
        st.write(
            f"{e.timestamp} · **{e.event_type}** · {e.message}"
        )
