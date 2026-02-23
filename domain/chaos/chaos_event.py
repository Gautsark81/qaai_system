from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChaosEvent:
    event_type: str      # FEED_GAP / LATENCY_SPIKE / BROKER_DOWN / PARTIAL_ACK
    source: str
    occurred_at: datetime
    details: str
