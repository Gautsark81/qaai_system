from domain.graduation.capital_scale_rule import CapitalScaleRule


def test_capital_scale_rule():
    assert CapitalScaleRule.next_capital(10000) == 15000
