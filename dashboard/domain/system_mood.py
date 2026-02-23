from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple


@dataclass(frozen=True)
class SystemMoodPenalties:
    violations: float
    telemetry: float
    determinism: float
    capital: float


@dataclass(frozen=True)
class SystemMoodResult:
    mood: int
    penalties: SystemMoodPenalties
    hard_gates: Dict[str, bool]
    computed_at: datetime
    samples: Tuple[int, ...] = ()  # ✅ backward compatible


# -----------------------------
# Phase-1.1 System Mood
# -----------------------------
def compute_system_mood(snapshot) -> SystemMoodResult:
    """
    Snapshot may be:
    - dict (real pipeline)
    - object with attributes (tests)
    """

    def _get(obj, key, default):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    violations_count = _get(_get(snapshot, "violations", {}), "count", 0)
    telemetry_completeness = _get(_get(snapshot, "telemetry", {}), "completeness", 1.0)
    replay_match_rate = _get(_get(snapshot, "determinism", {}), "replay_match_rate", 1.0)

    safety = _get(snapshot, "safety", {})
    execution_possible = _get(safety, "execution_possible", False)
    capital_allocated = _get(safety, "capital_allocated", 0.0)

    violation_penalty = min(violations_count * 20.0, 100.0)
    telemetry_penalty = (1.0 - telemetry_completeness) * 30.0
    determinism_penalty = (1.0 - replay_match_rate) * 40.0
    capital_penalty = min(capital_allocated, 100.0)

    now = datetime.utcnow()

    if execution_possible:
        return SystemMoodResult(
            mood=0,
            penalties=SystemMoodPenalties(
                violations=violation_penalty,
                telemetry=telemetry_penalty,
                determinism=determinism_penalty,
                capital=capital_penalty,
            ),
            hard_gates={"execution_possible": True},
            computed_at=now,
            samples=(0,),
        )

    raw_mood = (
        100.0
        - violation_penalty
        - telemetry_penalty
        - determinism_penalty
        - capital_penalty
    )

    mood = int(max(0, min(100, round(raw_mood))))

    return SystemMoodResult(
        mood=mood,
        penalties=SystemMoodPenalties(
            violations=violation_penalty,
            telemetry=telemetry_penalty,
            determinism=determinism_penalty,
            capital=capital_penalty,
        ),
        hard_gates={"execution_possible": False},
        computed_at=now,
        samples=(mood,),
    )
