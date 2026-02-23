from qaai_system.model_ops.retraining import RetrainingDecision


def test_retraining_decision_structure():
    d = RetrainingDecision(
        should_retrain=True,
        reasons=["decay_detected"],
        regime=None,
    )
    assert d.should_retrain is True
