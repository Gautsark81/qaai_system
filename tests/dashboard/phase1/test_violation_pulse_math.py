from datetime import datetime, timezone
from dashboard.analysis.violation_pulse import compute_violation_pulse
from dashboard.domain.system_mood import SystemMoodResult, SystemMoodPenalties
from dashboard.domain.system_mood_drift import SystemMoodDriftResult


def _mood(mood: float):
    return SystemMoodResult(
        mood=mood,
        penalties=SystemMoodPenalties(0, 0, 0, 0),
        hard_gates={"execution_possible": False},
        computed_at=datetime.now(timezone.utc),
    )


def _drift(slope=0.0, volatility=0.0, degrading=False):
    return SystemMoodDriftResult(
        mean=100.0,
        window=(100.0,),
        slope=slope,
        volatility=volatility,
        is_degrading=degrading,
        explanation="test",
        computed_at=datetime.now(timezone.utc),
    )


def test_pulse_calm_system():
    pulse = compute_violation_pulse(_mood(100), _drift())
    assert pulse.score == 0.0
    assert pulse.level == "CALM"


def test_pulse_detects_degrading_pressure():
    pulse = compute_violation_pulse(_mood(80), _drift(slope=-0.5, degrading=True))
    assert pulse.score > 0
    assert "negative_drift" in pulse.contributors
