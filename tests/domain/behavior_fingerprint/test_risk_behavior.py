from domain.behavior_fingerprint.risk_behavior import RiskExposureFingerprint
from domain.behavior_fingerprint.enums import RiskLevel


def test_risk_exposure_fingerprint():
    fp = RiskExposureFingerprint(
        max_position_pct=0.05,
        avg_leverage=2.0,
        stop_type="ATR",
        stop_distance_pct=0.01,
        tail_risk_exposure=RiskLevel.MEDIUM,
        capital_concentration=0.20,
    )

    assert fp.avg_leverage >= 1.0
    assert fp.tail_risk_exposure == RiskLevel.MEDIUM
