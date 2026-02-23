# core/evidence/audit_pdf_report.py

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

from core.evidence.audit_contracts import AuditReport


def generate_audit_report_pdf(
    *,
    report: AuditReport,
    output_path: str,
) -> None:
    """
    Generate a human-readable PDF audit report.
    """

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(
        f"<b>Audit Report — System {report.system_id}</b>",
        styles["Title"],
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        f"Generated at: {report.generated_at.isoformat()}",
        styles["Normal"],
    ))

    summary = report.summary
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    story.append(Paragraph(
        f"Period: {summary.start_time.isoformat()} → {summary.end_time.isoformat()}",
        styles["Normal"],
    ))
    story.append(Paragraph(
        f"Total decisions: {summary.total_decisions}",
        styles["Normal"],
    ))
    story.append(Paragraph(
        f"Strategies affected: {summary.strategies_affected}",
        styles["Normal"],
    ))
    story.append(Paragraph(
        f"Report checksum: {summary.report_checksum}",
        styles["Normal"],
    ))

    for section in report.sections:
        story.append(Spacer(1, 16))
        story.append(Paragraph(section.title, styles["Heading2"]))
        story.append(Paragraph(section.description, styles["Italic"]))

        for k, v in section.content.items():
            story.append(Paragraph(f"<b>{k}</b>: {v}", styles["Normal"]))

    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Methodology</b>", styles["Heading2"]))
    story.append(Paragraph(report.methodology, styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Limitations</b>", styles["Heading2"]))
    story.append(Paragraph(report.limitations, styles["Normal"]))

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
