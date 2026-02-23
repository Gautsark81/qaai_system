# core/operator/abuse_detection.py
from typing import List, Optional
from core.operator.operator_event import OperatorEvent, OperatorEventType
from core.operator.abuse_signal import OperatorAbuseSignal


def detect_override_abuse(
    operator_id: str,
    events: List[OperatorEvent],
    *,
    min_events: int = 5,
    override_ratio_threshold: float = 0.6,
    consecutive_override_threshold: int = 3,
) -> Optional[OperatorAbuseSignal]:
    """
    Detects override abuse patterns.
    Returns advisory signal or None.
    """

    relevant = [e for e in events if e.operator_id == operator_id]

    if len(relevant) < min_events:
        return None

    override_events = [
        (idx, e) for idx, e in enumerate(relevant)
        if e.event_type == OperatorEventType.OVERRIDE
    ]

    override_ratio = len(override_events) / len(relevant)

    # Rule 1: override dominance
    ratio_flag = override_ratio >= override_ratio_threshold

    # Rule 2: consecutive override streak
    max_streak = 0
    current = 0
    for e in relevant:
        if e.event_type == OperatorEventType.OVERRIDE:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0

    streak_flag = max_streak >= consecutive_override_threshold

    if not (ratio_flag or streak_flag):
        return None

    confidence = min(
        1.0,
        (override_ratio if ratio_flag else 0.0)
        + (0.2 if streak_flag else 0.0),
    )

    evidence_ids = [idx for idx, _ in override_events]

    return OperatorAbuseSignal(
        operator_id=operator_id,
        confidence=round(confidence, 2),
        reason="override abuse pattern detected",
        evidence_event_ids=evidence_ids,
    )
