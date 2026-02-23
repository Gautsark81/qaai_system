from core.screening.scorer import score_rules


def test_score_is_normalized_and_bounded():
    rules = {
        "r1": {"passed": True, "weight": 0.5},
        "r2": {"passed": False, "weight": 0.5},
    }

    score = score_rules(rules)

    assert 0.0 <= score <= 1.0


def test_zero_weight_safe():
    score = score_rules({})
    assert score == 0.0
