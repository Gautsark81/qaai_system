from modules.regime.policy import RegimePolicy


def test_policy_scales():
    p = RegimePolicy()
    assert p.scale_for("calm_trend") == 1.0
    assert p.scale_for("volatile_trend") < 1.0
    assert p.scale_for("panic") < p.scale_for("choppy")
