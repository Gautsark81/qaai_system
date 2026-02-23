# core/operator/abuse_signal.py
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class OperatorAbuseSignal:
    operator_id: str
    confidence: float          # 0.0 → 1.0
    reason: str
    evidence_event_ids: List[int]
