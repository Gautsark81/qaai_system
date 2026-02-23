from core.regime.signals import (
    compute_trend_strength,
    compute_volatility_ratio,
    compute_correlation_stress,
)


def test_trend_strength_positive_trend():
    returns = [1, 1, 1, 1]
    atr = 1.0

    val = compute_trend_strength(returns, atr)
    assert 0.9 <= val <= 1.0


def test_trend_strength_flat():
    returns = [0, 0, 0]
    atr = 1.0

    val = compute_trend_strength(returns, atr)
    assert val == 0.0


def test_trend_strength_clipped():
    returns = [10, 10, 10]
    atr = 0.1

    val = compute_trend_strength(returns, atr)
    assert val == 1.0


def test_volatility_ratio_normal():
    assert compute_volatility_ratio(2.0, 2.0) == 1.0


def test_volatility_ratio_high():
    assert compute_volatility_ratio(4.0, 2.0) == 2.0


def test_correlation_stress_low():
    corrs = [0.1, -0.2, 0.0]
    val = compute_correlation_stress(corrs)
    assert 0.0 <= val <= 0.3


def test_correlation_stress_high():
    corrs = [0.9, 0.8, 1.0]
    val = compute_correlation_stress(corrs)
    assert val >= 0.8
