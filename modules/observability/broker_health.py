# modules/observability/broker_health.py
from collections import defaultdict, deque
from statistics import mean
from typing import Dict


class BrokerHealthMonitor:
    """
    Rolling broker health statistics.
    Read-only. Observability only.
    """

    def __init__(self, window: int = 100):
        self._latencies = defaultdict(lambda: deque(maxlen=window))
        self._rejects = defaultdict(int)
        self._submits = defaultdict(int)

    def record_event(
        self,
        broker: str,
        event: str,
        latency_ms: float | None,
    ) -> None:
        if event == "submit":
            self._submits[broker] += 1

        if event == "reject":
            self._rejects[broker] += 1

        if latency_ms is not None:
            self._latencies[broker].append(latency_ms)

    def snapshot(self) -> Dict[str, dict]:
        snapshot = {}
        for broker in self._submits:
            lats = self._latencies[broker]
            snapshot[broker] = {
                "avg_latency_ms": mean(lats) if lats else None,
                "reject_rate": (
                    self._rejects[broker] / self._submits[broker]
                    if self._submits[broker] > 0
                    else 0.0
                ),
            }
        return snapshot
