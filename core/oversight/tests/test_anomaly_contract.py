from datetime import datetime

from core.oversight.contracts import OversightAnomaly


def test_anomaly_contract_fields():
    anomaly = OversightAnomaly(
        anomaly_id="an-1",
        anomaly_type="DRIFT",
        subject="capital",
        baseline_value=0.25,
        observed_value=0.40,
        deviation_pct=60.0,
        detected_at=datetime.utcnow(),
        metadata={"window_days": 5},
    )

    assert anomaly.deviation_pct > 0
    assert anomaly.metadata["window_days"] == 5
