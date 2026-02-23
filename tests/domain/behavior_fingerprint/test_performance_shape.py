from domain.behavior_fingerprint.performance_shape import PerformanceShapeFingerprint


def test_performance_shape_fingerprint():
    fp = PerformanceShapeFingerprint(
        win_rate_bucket="55-70",
        payoff_ratio_bucket="1-2",
        drawdown_profile="moderate",
        equity_curve_shape="smooth",
    )

    assert fp.win_rate_bucket != ""
