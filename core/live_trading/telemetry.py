from dataclasses import dataclass
from time import time


@dataclass(frozen=True)
class ExecutionSample:
    symbol: str
    paper_price: float
    live_price: float
    timestamp: float


class TelemetryCollector:
    """
    Collects execution telemetry (append-only).
    """

    def __init__(self):
        self.samples: list[ExecutionSample] = []

    def record(
        self,
        *,
        symbol: str,
        paper_price: float,
        live_price: float,
    ):
        self.samples.append(
            ExecutionSample(
                symbol=symbol,
                paper_price=paper_price,
                live_price=live_price,
                timestamp=time(),
            )
        )
