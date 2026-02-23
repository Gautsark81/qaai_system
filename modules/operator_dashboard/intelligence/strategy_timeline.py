from typing import List, Dict

from core.telemetry.metrics_history_store import MetricsHistoryStore
from core.operations.ops_store import OpsEventStore


class StrategyBehaviorTimelineBuilder:
    """
    Builds a chronological, read-only narrative of a strategy's behavior.

    Design rules:
    - Consume persisted facts only
    - No execution imports
    - No live trading modules
    - No governance logic coupling
    """

    def __init__(
        self,
        metrics_store: MetricsHistoryStore | None = None,
        ops_store: OpsEventStore | None = None,
    ):
        self.metrics_store = metrics_store or MetricsHistoryStore()
        self.ops_store = ops_store or OpsEventStore()

    def build(self, strategy_id: str) -> List[Dict]:
        events: List[Dict] = []

        # 1. Metrics history (behavior over time)
        for snap in self.metrics_store.load(strategy_id):
            events.append(
                {
                    "type": "metrics",
                    "source": snap["source"],
                    "ssr": snap["ssr"],
                    "total_trades": snap["total_trades"],
                    "recorded_at": snap["recorded_at"],
                }
            )

        # 2. Operational events (kill-switch drills, ops checks)
        for op in self.ops_store.load_all():
            notes = op.get("notes", "")
            if strategy_id in notes:
                events.append(
                    {
                        "type": "ops",
                        "event_type": op["event_type"],
                        "recorded_at": op["occurred_at"],
                        "notes": notes,
                    }
                )

        # Chronological ordering is the only "logic" allowed here
        events.sort(key=lambda e: e["recorded_at"])

        return events
