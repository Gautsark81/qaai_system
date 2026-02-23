from core.regime.state_machine.transition_tracker import compute_transition_score


def test_transition_score_basic():
    score = compute_transition_score(0.2, 0.1, 0.1)
    assert 0 <= score <= 1


def test_transition_clipped():
    score = compute_transition_score(5, 5, 5)
    assert score == 1.0