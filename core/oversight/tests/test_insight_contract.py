from datetime import datetime

from core.oversight.contracts import OversightInsight, OversightObservation


def test_insight_aggregation():
    obs = OversightObservation(
        observation_id="obs-3",
        category="GOVERNANCE",
        severity="WARNING",
        summary="Approval lag detected",
        explanation="Median approval time increased",
        evidence_refs=["dec-7"],
        detected_at=datetime.utcnow(),
    )

    insight = OversightInsight(
        insight_id="ins-1",
        title="Governance Friction",
        summary="Governance latency is increasing",
        observations=[obs],
        severity="WARNING",
        generated_at=datetime.utcnow(),
    )

    assert len(insight.observations) == 1
    assert insight.severity == "WARNING"
