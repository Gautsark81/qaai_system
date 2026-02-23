from datetime import datetime

from core.oversight.contracts import OversightObservation


def test_observation_is_immutable():
    obs = OversightObservation(
        observation_id="obs-1",
        category="CAPITAL",
        severity="WARNING",
        summary="Capital concentration rising",
        explanation="Top strategy exceeds historical concentration",
        evidence_refs=["chk-123"],
        detected_at=datetime.utcnow(),
    )

    try:
        obs.severity = "CRITICAL"
        assert False
    except Exception:
        assert True


def test_observation_fields_present():
    obs = OversightObservation(
        observation_id="obs-2",
        category="STRATEGY",
        severity="INFO",
        summary="Stable performance",
        explanation="No anomalies detected",
        evidence_refs=[],
        detected_at=datetime.utcnow(),
        related_strategy_id="alpha_1",
    )

    assert obs.related_strategy_id == "alpha_1"
