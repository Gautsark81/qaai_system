from typing import Dict, Optional
from datetime import datetime, timezone

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.operations.ops_store import OpsEventStore


class CanaryHealthAggregator:
    """
    Computes non-PnL canary health metrics.

    Principles:
    - Observational only
    - No thresholds
    - No decisions
    - No capital logic
    """

    def __init__(
        self,
        metrics_store: MetricsHistoryStore | None = None,
        ops_store: OpsEventStore | None = None,
    ):
        self.metrics_store = metrics_store or MetricsHistoryStore()
        self.ops_store = ops_store or OpsEventStore()

    def compute(self, strategy_id: str) -> Dict:
        """
        Returns aggregated canary health facts.
        """
        metrics = self.metrics_store.load(strategy_id)
        ops = self.ops_store.load_all()

        canary_metrics = [
            m for m in metrics if m["source"] == "live"
        ]

        first_seen: Optional[datetime] = None
        last_seen: Optional[datetime] = None

        for m in canary_metrics:
            ts = datetime.fromisoformat(m["recorded_at"])
            if not first_seen or ts < first_seen:
                first_seen = ts
            if not last_seen or ts > last_seen:
                last_seen = ts

        time_in_canary_hours: Optional[float] = None
        if first_seen and last_seen:
            delta = last_seen - first_seen
            time_in_canary_hours = delta.total_seconds() / 3600.0

        kill_events = [
            e for e in ops
            if e["event_type"] == "kill_switch_drill"
            and strategy_id in e.get("notes", "")
        ]

        ops_mentions = [
            e for e in ops
            if strategy_id in e.get("notes", "")
        ]

        return {
            "strategy_id": strategy_id,
            "time_in_canary_hours": time_in_canary_hours,
            "canary_snapshots": len(canary_metrics),
            "kill_switch_events": len(kill_events),
            "ops_mentions": len(ops_mentions),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
