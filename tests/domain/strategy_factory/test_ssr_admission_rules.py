from domain.strategy_factory.ssr_admission_rules import SSRAdmissionRules


def test_ssr_below_threshold_blocked():
    res = SSRAdmissionRules.validate(0.75)
    assert res.valid is False


def test_ssr_above_threshold_allowed():
    res = SSRAdmissionRules.validate(0.85)
    assert res.valid is True
