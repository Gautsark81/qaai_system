from dataclasses import dataclass


@dataclass(frozen=True)
class LatencyMetrics:
    order_to_ack_ms: float
    data_latency_ms: float
