from modules.strategy_health.decay_detector import DecayDetector
from modules.strategy_health.evaluator import HealthResult


def _hr(h, wr, dd):
    return HealthResult(
        strategy_id="s1",
        health_score=h,
        signals={
            "win_rate": wr,
            "expectancy": 0.6,
            "drawdown": dd,
            "consistency": 0.7,
            "activity": 0.8,
        },
        flags=[],
        window=50,
        reason="test",
    )


def test_no_decay_with_insufficient_history():
    detector = DecayDetector()
    history = [_hr(0.9, 1.0, 1.0)] * 40

    signal = detector.evaluate(history)

    assert signal.level == "NO_DECAY"


def test_soft_decay_single_dimension():
    detector = DecayDetector()

    history = []
    history += [_hr(0.9, 1.0, 1.0)] * 30
    history += [_hr(0.7, 1.0, 1.0)] * 30

    signal = detector.evaluate(history)

    assert signal.level == "SOFT_DECAY"
    assert "Health score trending downward" in signal.reasons


def test_hard_decay_two_dimensions():
    detector = DecayDetector()

    history = []
    history += [_hr(0.9, 1.0, 1.0)] * 60
    history += [_hr(0.6, 0.6, 0.7)] * 60

    signal = detector.evaluate(history)

    assert signal.level in {"HARD_DECAY", "STRUCTURAL_DECAY"}
    assert len(signal.reasons) >= 2


def test_structural_decay_long_window():
    detector = DecayDetector()

    history = []
    history += [_hr(0.9, 1.0, 1.0)] * 120
    history += [_hr(0.5, 0.4, 0.4)] * 120

    signal = detector.evaluate(history)

    assert signal.level == "STRUCTURAL_DECAY"
    assert 120 in signal.windows_confirmed
