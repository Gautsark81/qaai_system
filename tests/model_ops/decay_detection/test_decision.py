from qaai_system.model_ops.decay_detection import DecayDecision


def test_decay_decision_flags():
    decision = DecayDecision(decaying=True, reasons=["X"])
    assert decision.decaying is True
    assert decision.reasons == ["X"]
