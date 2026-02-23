from core.screening.decision import make_decision


def test_decision_passes_above_threshold():
    rules = {
        "a": {"passed": True},
        "b": {"passed": True},
    }

    passed, reasons = make_decision(score=0.9, rules=rules)

    assert passed is True
    assert len(reasons) == 2


def test_decision_blocks_below_threshold():
    rules = {
        "a": {"passed": False},
        "b": {"passed": True},
    }

    passed, reasons = make_decision(score=0.3, rules=rules)

    assert passed is False
