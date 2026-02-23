import streamlit as st
import pandas as pd
from modules.operator_dashboard.runtime import get_runtime_snapshot


def render_strategies_page():
    st.title("📊 Strategy Intelligence")

    state = get_runtime_snapshot()

    if not state.strategies:
        st.warning("No strategies available.")
        return

    df = pd.DataFrame(
        [
            {
                "Strategy": s.strategy_id,
                "Lifecycle": getattr(s, "lifecycle_stage", None),
                "SSR": getattr(s, "ssr", None),
                "Capital %": getattr(s, "capital_allocated_pct", None),
                "Confidence": getattr(s, "confidence_score", None),
            }
            for s in state.strategies
        ]
    )

    st.dataframe(df, use_container_width=True)

    st.divider()

    st.subheader("Allocation Heatmap")
    st.bar_chart(df.set_index("Strategy")["Capital %"])