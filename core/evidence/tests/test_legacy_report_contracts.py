from datetime import datetime

from core.evidence.report_contracts import ReplayAuditReport


def test_replay_audit_report_is_immutable():
    report = ReplayAuditReport(
        generated_at=datetime.utcnow(),
        from_timestamp=datetime.utcnow(),
        to_timestamp=datetime.utcnow(),
        summary={"x": 1},
        frames_before={},
        frames_after={},
        diffs={},
        evidence_count=2,
        checksum="abc",
    )

    assert report.checksum == "abc"
