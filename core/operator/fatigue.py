# core/operator/fatigue.py
from typing import List
from core.operator.operator_event import OperatorEvent


def compute_fatigue_level(
    events: List[OperatorEvent],
    *,
    short_window_minutes: int = 15,
    long_window_minutes: int = 120,
    min_short_events: int = 3,
    min_long_events: int = 10,
) -> float:
    """
    Fatigue ∈ [0.0, 1.0]

    Rules:
    - No fatigue below minimum activity
    - Burst activity dominates sustained activity
    - Deterministic and replay-safe
    """

    if not events:
        return 0.0

    now_ts = max(e.timestamp for e in events).timestamp()

    short_cutoff = now_ts - short_window_minutes * 60
    long_cutoff = now_ts - long_window_minutes * 60

    short_events = [
        e for e in events if e.timestamp.timestamp() >= short_cutoff
    ]
    long_events = [
        e for e in events if e.timestamp.timestamp() >= long_cutoff
    ]

    burst_fatigue = 0.0
    if len(short_events) >= min_short_events:
        burst_density = len(short_events) / short_window_minutes
        burst_fatigue = min(1.0, burst_density / 0.3)

    sustained_fatigue = 0.0
    if len(long_events) >= min_long_events:
        sustained_density = len(long_events) / long_window_minutes
        sustained_fatigue = min(1.0, sustained_density / 0.25)

    fatigue = max(burst_fatigue, sustained_fatigue)
    return round(fatigue, 3)
