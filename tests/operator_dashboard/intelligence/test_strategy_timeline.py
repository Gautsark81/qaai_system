from pathlib import Path

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.telemetry.metrics_snapshot import MetricsSnapshot
from core.operations.ops_store import OpsEventStore
from core.operations.ops_events import OpsEvent
from modules.operator_dashboard.intelligence.strategy_timeline import (
    StrategyBehaviorTimelineBuilder,
)


def test_strategy_behavior_timeline(tmp_path: Path):
    metrics = MetricsHistoryStore(root_dir=tmp_path / "metrics")
    ops = OpsEventStore(root_dir=tmp_path / "ops")

    metrics.append(
        MetricsSnapshot.now(
            strategy_id="s1",
            source="backtest",
            ssr=0.82,
            total_trades=200,
        )
    )

    ops.append(
        OpsEvent.now(
            event_type="daily_check",
            operator="tester",
            notes="Checked s1 — behavior normal",
        )
    )

    builder = StrategyBehaviorTimelineBuilder(
        metrics_store=metrics,
        ops_store=ops,
    )

    timeline = builder.build("s1")

    assert len(timeline) == 2
    assert timeline[0]["type"] in {"metrics", "ops"}
