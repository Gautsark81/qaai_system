# tests/strategy_tournament/test_correlation.py

from modules.strategy_tournament.correlation import pnl_correlation


def test_zero_length_series():
    assert pnl_correlation([], []) == 0.0
    assert pnl_correlation([1], [1]) == 0.0


def test_identical_series_high_correlation():
    a = [1, 2, 3, 4, 5]
    b = [1, 2, 3, 4, 5]
    corr = pnl_correlation(a, b)
    assert corr > 0.99


def test_inverse_series_negative_correlation():
    a = [1, 2, 3, 4, 5]
    b = [-1, -2, -3, -4, -5]
    corr = pnl_correlation(a, b)
    assert corr < -0.99


def test_uncorrelated_series_near_zero():
    a = [1, -1, 1, -1, 1]
    b = [1, 1, -1, -1, 1]
    corr = pnl_correlation(a, b)
    assert abs(corr) < 0.5
