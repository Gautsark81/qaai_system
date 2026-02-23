from datetime import datetime
from dashboard.domain.violation_pulse import ViolationPulseResult
from dashboard.domain.system_mood import SystemMoodResult
from dashboard.domain.system_mood_drift import SystemMoodDriftResult


def compute_violation_pulse(
    mood: SystemMoodResult,
    drift: SystemMoodDriftResult,
) -> ViolationPulseResult:
    """
    Phase-1.3 Violation Pulse (Safety Pressure Index)

    Deterministic, snapshot-only, read-only.
    """

    score = 0.0
    contributors = []

    # Base pressure from mood degradation
    score += max(0.0, 100.0 - mood.mood) * 0.5
    if mood.mood < 100:
        contributors.append("mood_penalty")

    # Drift pressure
    if drift.is_degrading:
        score += min(abs(drift.slope) * 50.0, 25.0)
        contributors.append("negative_drift")

    # Volatility pressure
    if drift.volatility > 0:
        score += min(drift.volatility * 10.0, 20.0)
        contributors.append("volatility")

    # Hard gate amplification (informational only)
    if mood.hard_gates.get("execution_possible") is False:
        contributors.append("execution_blocked")

    return ViolationPulseResult(
        score=round(min(score, 100.0), 2),
        contributors=tuple(contributors),
        computed_at=mood.computed_at,
    )
