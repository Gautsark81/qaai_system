from modules.promotion.capital_ramp import capital_ramp


def test_capital_ramp():
    assert capital_ramp(1) == 0.10
    assert capital_ramp(7) == 0.50
    assert capital_ramp(20) == 1.00
