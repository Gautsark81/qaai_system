from domain.meta_model.read_only_guard import ReadOnlyGuard
from domain.meta_model.probability_output import ProbabilityOutput


def test_read_only_guard_accepts_probability_output():
    p = ProbabilityOutput(
        p_up=0.5,
        p_down=0.5,
        confidence=0.0,
        feature_importance={},
        model_version="v",
    )
    ReadOnlyGuard.assert_read_only(p)
