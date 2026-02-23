from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class ExecutionStyleFingerprint:
    order_types: Set[str]
    slippage_sensitivity: str
    latency_tolerance_ms: int
    partial_fill_handling: str
