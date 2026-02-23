from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence, Tuple, Optional


# ─────────────────────────────────────────────
# Shared Sample (USED BY ANALYSIS LAYER)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class SystemMoodSample:
    mood: float
    timestamp: datetime


# ─────────────────────────────────────────────
# Canonical Drift Result (SUPERSET CONTRACT)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class SystemMoodDriftResult:
    """
    Canonical System Mood Drift Result.

    Supports:
    - Phase-1 observational drift
    - Statistical analysis drift
    """

    # Always present
    mean: float
    computed_at: datetime = datetime.min.replace(tzinfo=timezone.utc)

    # Phase-1
    window: Tuple[float, ...] = ()

    # Analysis-only (optional but supported)
    window_size: int = 0
    samples: Tuple[SystemMoodSample, ...] = ()
    slope: float = 0.0
    volatility: float = 0.0
    is_degrading: bool = False
    explanation: Optional[str] = None


# ─────────────────────────────────────────────
# Phase-1.2 Drift (OBSERVATIONAL ONLY)
# ─────────────────────────────────────────────

def compute_system_mood_drift(system_mood_detail) -> SystemMoodDriftResult:
    """
    Phase-1.2 canonical drift computation.

    Rules:
    - Deterministic
    - Snapshot-only
    - No statistics
    - No history
    """

    return SystemMoodDriftResult(
        mean=system_mood_detail.mood,
        window=(system_mood_detail.mood,),
        computed_at=system_mood_detail.computed_at,
    )
