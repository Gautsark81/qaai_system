from dataclasses import dataclass


@dataclass(frozen=True)
class RollbackMetrics:
    max_drawdown: float
    es_95: float
    sharpe: float
    latency_p99_ms: float
    error_rate: float


class RollbackRule:
    """
    Pure, deterministic rule.
    Returns True if rollback should be triggered.
    """

    def evaluate(self, metrics: RollbackMetrics) -> bool:
        raise NotImplementedError

class MaxDrawdownRule(RollbackRule):
    def __init__(self, limit: float):
        self.limit = limit

    def evaluate(self, metrics: RollbackMetrics) -> bool:
        return metrics.max_drawdown > self.limit


class ErrorRateRule(RollbackRule):
    def evaluate(self, metrics: RollbackMetrics) -> bool:
        return metrics.error_rate > 0.0


class LatencyRule(RollbackRule):
    def __init__(self, limit_ms: float):
        self.limit_ms = limit_ms

    def evaluate(self, metrics: RollbackMetrics) -> bool:
        return metrics.latency_p99_ms > self.limit_ms
