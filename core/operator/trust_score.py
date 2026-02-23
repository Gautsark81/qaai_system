# core/operator/trust_score.py
from dataclasses import dataclass
from typing import List
from core.operator.operator_event import OperatorEvent, OperatorEventType
from core.operator.fatigue import compute_fatigue_level


@dataclass(frozen=True)
class OperatorTrustScore:
    operator_id: str
    trust: float          # 0.0 → 1.0
    fatigue: float        # 0.0 → 1.0


def compute_trust_score(
    operator_id: str,
    events: List[OperatorEvent],
    *,
    base_decay: float = 0.05,
    recovery_rate: float = 0.02,
) -> OperatorTrustScore:
    """
    Computes trust score with fatigue-weighted decay.
    """

    trust = 1.0
    relevant = [e for e in events if e.operator_id == operator_id]
    fatigue = compute_fatigue_level(relevant)

    for e in relevant:
        if e.event_type == OperatorEventType.OVERRIDE:
            decay = base_decay * (1.0 + fatigue)
            trust -= decay
        else:
            trust += recovery_rate

        trust = min(1.0, max(0.0, trust))

    return OperatorTrustScore(
        operator_id=operator_id,
        trust=round(trust, 3),
        fatigue=fatigue,
    )
