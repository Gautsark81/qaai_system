from core.regime.state_machine.break_detector import compute_break_score


def test_break_score_computation():
    score = compute_break_score(1, 1, 1)
    assert score == 1.0


def test_break_score_zero():
    score = compute_break_score(0, 0, 0)
    assert score == 0.0