from datetime import datetime, timedelta, timezone

from dashboard.analysis.system_mood_drift import compute_system_mood_drift
from dashboard.domain.system_mood_drift import SystemMoodSample


def _sample(ts_offset: int, mood: float) -> SystemMoodSample:
    return SystemMoodSample(
        timestamp=datetime.now(tz=timezone.utc) + timedelta(seconds=ts_offset),
        mood=mood,
    )


def test_drift_single_sample_is_stable_and_explainable():
    samples = [_sample(0, 80.0)]

    drift = compute_system_mood_drift(samples)

    assert drift.window_size == 1
    assert drift.mean == 80.0
    assert drift.slope == 0.0
    assert drift.volatility == 0.0
    assert drift.is_degrading is False
    assert drift.explanation
    assert "last 1 snapshots" in drift.explanation


def test_drift_detects_downward_trend():
    samples = [
        _sample(0, 90.0),
        _sample(1, 85.0),
        _sample(2, 80.0),
        _sample(3, 75.0),
    ]

    drift = compute_system_mood_drift(samples)

    assert drift.window_size == 4
    assert drift.mean == 82.5
    assert drift.slope < 0
    assert drift.is_degrading is True
    assert drift.volatility > 0
    assert "trending down" in drift.explanation.lower()


def test_drift_detects_upward_trend():
    samples = [
        _sample(0, 60.0),
        _sample(1, 65.0),
        _sample(2, 70.0),
        _sample(3, 75.0),
    ]

    drift = compute_system_mood_drift(samples)

    assert drift.slope > 0
    assert drift.is_degrading is False
    assert "up or stable" in drift.explanation.lower()


def test_drift_flat_series_is_stable():
    samples = [
        _sample(0, 70.0),
        _sample(1, 70.0),
        _sample(2, 70.0),
    ]

    drift = compute_system_mood_drift(samples)

    assert drift.slope == 0.0
    assert drift.volatility == 0.0
    assert drift.is_degrading is False


def test_drift_empty_input_is_safe():
    drift = compute_system_mood_drift([])

    assert drift.window_size == 0
    assert drift.mean == 0.0
    assert drift.slope == 0.0
    assert drift.volatility == 0.0
    assert drift.is_degrading is False
    assert drift.explanation
