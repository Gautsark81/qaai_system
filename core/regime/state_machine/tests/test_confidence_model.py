from core.regime.state_machine.confidence_model import compute_confidence_score


def test_confidence_high_when_stable():
    conf = compute_confidence_score(0.9, 20, 0.0)
    assert conf > 0.8


def test_confidence_drops_with_break():
    conf = compute_confidence_score(0.9, 20, 1.0)
    assert conf < 0.7