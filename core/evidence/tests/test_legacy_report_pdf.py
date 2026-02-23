# core/evidence/tests/test_legacy_report_pdf.py

from datetime import datetime

from core.evidence.report_pdf import export_report_pdf
from core.evidence.report_contracts import ReplayAuditReport, ReportSummary


def make_sample_report():
    return ReplayAuditReport(
        generated_at=datetime.utcnow(),
        from_timestamp=datetime(2024, 1, 1),
        to_timestamp=datetime(2024, 1, 2),
        evidence_count=3,
        checksum="abc123",

        # ✅ REQUIRED summary
        summary=ReportSummary(
            decisions_total=3,
            decisions_approved=2,
            decisions_rejected=1,
            anomalies_detected=0,
            notes="Test summary",
        ),

        frames_before={},
        frames_after={},
        diffs={},
    )


def test_export_report_pdf_returns_bytes_without_reportlab():
    """
    PDF export MUST succeed even if reportlab is not installed.
    """
    report = make_sample_report()
    pdf = export_report_pdf(report=report)

    assert isinstance(pdf, bytes)
    assert len(pdf) > 0
