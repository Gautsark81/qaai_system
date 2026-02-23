# core/oversight/tests/test_correlation_engine.py

from datetime import datetime, timedelta

from core.oversight.correlation.engine import correlate_findings
from core.oversight.contracts.finding import OversightFinding


def make_finding(
    *,
    domain: str,
    severity: str,
    summary: str,
    detector: str,
    evidence_id: str = None,
):
    return OversightFinding(
        domain=domain,
        severity=severity,
        summary=summary,
        detector=detector,
        evidence_id=evidence_id,
    )


def test_correlation_not_triggered_with_single_domain():
    findings = [
        make_finding(
            domain="capital",
            severity="WARNING",
            summary="Capital drift detected",
            detector="CapitalDriftDetector",
        )
    ]

    event = correlate_findings(
        event_id="evt-1",
        generated_at=datetime.utcnow(),
        findings=findings,
    )

    assert event is None


def test_correlation_triggers_with_multiple_domains():
    findings = [
        make_finding(
            domain="capital",
            severity="WARNING",
            summary="Capital drift detected",
            detector="CapitalDriftDetector",
            evidence_id="e1",
        ),
        make_finding(
            domain="governance",
            severity="INFO",
            summary="Governance latency rising",
            detector="GovernanceFrictionDetector",
            evidence_id="e2",
        ),
    ]

    event = correlate_findings(
        event_id="evt-2",
        generated_at=datetime.utcnow(),
        findings=findings,
    )

    assert event is not None
    assert event.severity == "WARNING"
    assert event.requires_human_attention is True
    assert event.involved_domains == {"capital", "governance"}
    assert "Capital drift detected" in event.contributing_findings


def test_severity_escalates_to_critical():
    findings = [
        make_finding(
            domain="capital",
            severity="WARNING",
            summary="Capital drift detected",
            detector="CapitalDriftDetector",
        ),
        make_finding(
            domain="lifecycle",
            severity="CRITICAL",
            summary="Lifecycle oscillation detected",
            detector="LifecycleAnomalyDetector",
        ),
    ]

    event = correlate_findings(
        event_id="evt-3",
        generated_at=datetime.utcnow(),
        findings=findings,
    )

    assert event.severity == "CRITICAL"
    assert event.requires_human_attention is True


def test_info_only_correlation_does_not_require_attention():
    findings = [
        make_finding(
            domain="capital",
            severity="INFO",
            summary="Minor allocation shift",
            detector="CapitalDriftDetector",
        ),
        make_finding(
            domain="governance",
            severity="INFO",
            summary="Normal approval latency",
            detector="GovernanceFrictionDetector",
        ),
    ]

    event = correlate_findings(
        event_id="evt-4",
        generated_at=datetime.utcnow(),
        findings=findings,
    )

    assert event is not None
    assert event.severity == "INFO"
    assert event.requires_human_attention is False


def test_correlation_is_deterministic():
    findings = [
        make_finding(
            domain="capital",
            severity="WARNING",
            summary="Capital drift detected",
            detector="CapitalDriftDetector",
        ),
        make_finding(
            domain="governance",
            severity="WARNING",
            summary="Approval backlog",
            detector="GovernanceFrictionDetector",
        ),
    ]

    t = datetime.utcnow()

    e1 = correlate_findings(
        event_id="evt-x",
        generated_at=t,
        findings=findings,
    )

    e2 = correlate_findings(
        event_id="evt-x",
        generated_at=t,
        findings=findings,
    )

    assert e1 == e2
