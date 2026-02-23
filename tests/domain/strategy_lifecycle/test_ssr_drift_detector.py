from domain.strategy_lifecycle.ssr_drift_detector import SSRDriftDetector


def test_ssr_drift_detected():
    assert SSRDriftDetector.is_degraded(0.60, 0.80) is True


def test_ssr_stable():
    assert SSRDriftDetector.is_degraded(0.78, 0.80) is False
