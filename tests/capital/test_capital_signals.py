from modules.capital.signals import CapitalSignals


def test_drawdown_signal_monotonic():
    s1 = CapitalSignals.drawdown([100, 110, 105], 0.2, 0.2)
    s2 = CapitalSignals.drawdown([100, 120, 80], 0.2, 0.2)

    assert s2.scale <= s1.scale


def test_cash_signal_bounds():
    low = CapitalSignals.cash_ratio(0.05)
    high = CapitalSignals.cash_ratio(0.8)

    assert low.scale < high.scale
