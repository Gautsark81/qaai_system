"""
modules/performance/registry.py

Collects runtime performance samples.
OBSERVABILITY ONLY — NEVER affects logic.
"""

from collections import defaultdict


class PerformanceRegistry:
    def __init__(self):
        self._samples = defaultdict(list)

    def record(self, name: str, latency_ms: float):
        self._samples[name].append(latency_ms)

    def max_latency(self, name: str) -> float:
        if not self._samples[name]:
            return 0.0
        return max(self._samples[name])
