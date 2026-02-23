from datetime import datetime

from core.evidence.report_json import export_report_json
from core.evidence.report_contracts import ReplayAuditReport


def test_export_report_json_roundtrip():
    report = ReplayAuditReport(
        generated_at=datetime.utcnow(),
        from_timestamp=datetime.utcnow(),
        to_timestamp=datetime.utcnow(),
        summary={"ok": True},
        frames_before={},
        frames_after={},
        diffs={},
        evidence_count=1,
        checksum="xyz",
    )

    output = export_report_json(report=report)

    assert '"checksum": "xyz"' in output
