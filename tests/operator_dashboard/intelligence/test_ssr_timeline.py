from pathlib import Path

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.telemetry.metrics_snapshot import MetricsSnapshot
from modules.operator_dashboard.intelligence.ssr_timeline import (
    SSRTimelineBuilder,
)


def test_ssr_timeline_build(tmp_path: Path):
    store = MetricsHistoryStore(root_dir=tmp_path)

    store.append(
        MetricsSnapshot.now(
            strategy_id="s1",
            source="backtest",
            ssr=0.76,
            total_trades=200,
        )
    )
    store.append(
        MetricsSnapshot.now(
            strategy_id="s1",
            source="paper",
            ssr=0.81,
            total_trades=90,
        )
    )

    builder = SSRTimelineBuilder(store)
    timeline = builder.build("s1")

    assert len(timeline) == 2
    assert timeline[0]["source"] == "backtest"
    assert timeline[1]["ssr"] == 0.81
