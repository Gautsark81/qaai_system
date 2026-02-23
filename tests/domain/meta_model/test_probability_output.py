from domain.meta_model.probability_output import ProbabilityOutput


def test_probability_output_bounds():
    p = ProbabilityOutput(
        p_up=0.6,
        p_down=0.4,
        confidence=0.8,
        feature_importance={"rsi": 0.2},
        model_version="v1",
    )
    assert 0.0 <= p.p_up <= 1.0
    assert 0.0 <= p.p_down <= 1.0
