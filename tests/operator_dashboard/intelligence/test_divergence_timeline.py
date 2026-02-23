import pytest
from pathlib import Path

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.telemetry.metrics_snapshot import MetricsSnapshot
from modules.operator_dashboard.intelligence.divergence_timeline import (
    DivergenceTimelineBuilder,
)


def test_divergence_timeline(tmp_path: Path):
    store = MetricsHistoryStore(root_dir=tmp_path)

    store.append(
        MetricsSnapshot.now(
            strategy_id="s1",
            source="backtest",
            ssr=0.80,
            total_trades=250,
        )
    )
    store.append(
        MetricsSnapshot.now(
            strategy_id="s1",
            source="paper",
            ssr=0.74,
            total_trades=100,
            latency_ms=48.0,
            slippage_pct=0.06,
        )
    )

    builder = DivergenceTimelineBuilder(store)
    timeline = builder.build("s1")

    assert len(timeline) == 1
    assert timeline[0]["delta_ssr"] == pytest.approx(-0.06)
    assert timeline[0]["latency_ms"] == 48.0
