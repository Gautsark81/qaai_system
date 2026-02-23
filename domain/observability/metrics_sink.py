from typing import Dict, List


class MetricsSink:
    """
    Collects structured metrics (no side effects).
    """

    def __init__(self):
        self._metrics: List[Dict] = []

    def emit(self, metric: Dict) -> None:
        self._metrics.append(metric)

    def all(self) -> List[Dict]:
        return list(self._metrics)
