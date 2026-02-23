from domain.behavior_fingerprint.stability import StabilityFingerprint
from domain.behavior_fingerprint.enums import StabilityLevel


def test_stability_fingerprint():
    fp = StabilityFingerprint(
        parameter_sensitivity=StabilityLevel.LOW,
        regime_dependence=StabilityLevel.MODERATE,
        sample_efficiency=StabilityLevel.HIGH,
        backtest_variance=StabilityLevel.STABLE,
    )

    assert fp.backtest_variance == StabilityLevel.STABLE
