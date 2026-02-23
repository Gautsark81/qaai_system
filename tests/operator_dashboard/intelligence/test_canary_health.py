from pathlib import Path

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.telemetry.metrics_snapshot import MetricsSnapshot
from core.operations.ops_store import OpsEventStore
from core.operations.ops_events import OpsEvent
from modules.operator_dashboard.intelligence.canary_health import (
    CanaryHealthAggregator,
)


def test_canary_health_aggregation(tmp_path: Path):
    metrics = MetricsHistoryStore(root_dir=tmp_path / "metrics")
    ops = OpsEventStore(root_dir=tmp_path / "ops")

    metrics.append(
        MetricsSnapshot.now(
            strategy_id="s1",
            source="live",
            ssr=0.81,
            total_trades=20,
        )
    )

    ops.append(
        OpsEvent.now(
            event_type="kill_switch_drill",
            operator="tester",
            notes="Drill for s1 completed",
        )
    )

    agg = CanaryHealthAggregator(
        metrics_store=metrics,
        ops_store=ops,
    )

    health = agg.compute("s1")

    assert health["strategy_id"] == "s1"
    assert health["canary_snapshots"] == 1
    assert health["kill_switch_events"] == 1
    assert health["ops_mentions"] >= 1
