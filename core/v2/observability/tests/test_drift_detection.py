from core.v2.observability.drift_detection import DriftDetector


def test_detects_high_drift():
    d = DriftDetector()
    baseline = {"ssr": 0.85}
    current = {"ssr": 0.70}

    signals = d.detect(baseline, current)
    assert signals[0].severity == "HIGH"
