# modules/observability/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class BrokerExecutionMetric:
    timestamp: datetime
    broker: str
    event: str  # submit | ack | fill | reject | timeout
    latency_ms: Optional[float]
    order_id: str
    symbol: str
