from typing import Dict, List, Optional

from core.telemetry.metrics_history_store import MetricsHistoryStore


class DivergenceTimelineBuilder:
    """
    Computes paper vs backtest divergence over time.
    Read-only, no thresholds, no judgments.
    """

    def __init__(self, store: MetricsHistoryStore | None = None):
        self.store = store or MetricsHistoryStore()

    def build(self, strategy_id: str) -> List[Dict]:
        history = self.store.load(strategy_id)

        backtest_ssr: Optional[float] = None
        timeline: List[Dict] = []

        for rec in history:
            if rec["source"] == "backtest":
                backtest_ssr = rec["ssr"]

            if rec["source"] == "paper" and backtest_ssr is not None:
                timeline.append(
                    {
                        "recorded_at": rec["recorded_at"],
                        "paper_ssr": rec["ssr"],
                        "backtest_ssr": backtest_ssr,
                        "delta_ssr": rec["ssr"] - backtest_ssr,
                        "latency_ms": rec.get("latency_ms"),
                        "slippage_pct": rec.get("slippage_pct"),
                    }
                )

        return timeline
