from typing import List, Dict

from core.telemetry.metrics_history_store import MetricsHistoryStore


class SSRTimelineBuilder:
    """
    Builds read-only SSR timelines from metrics history.
    """

    def __init__(self, store: MetricsHistoryStore | None = None):
        self.store = store or MetricsHistoryStore()

    def build(self, strategy_id: str) -> List[Dict]:
        """
        Returns a chronological SSR timeline.
        """
        history = self.store.load(strategy_id)

        timeline = []
        for rec in history:
            timeline.append(
                {
                    "recorded_at": rec["recorded_at"],
                    "source": rec["source"],
                    "ssr": rec["ssr"],
                    "total_trades": rec["total_trades"],
                }
            )

        return timeline
