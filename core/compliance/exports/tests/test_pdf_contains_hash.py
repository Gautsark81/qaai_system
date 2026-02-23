from core.compliance.exports.pdf_export import PDFAuditExporter
from core.compliance.exports.contracts import AuditExport, ExportMetadata, ExportSeal

def test_pdf_contains_cryptographic_hash():
    export = AuditExport(
        metadata=ExportMetadata(
            export_version="1.0",
            export_type="AUDIT",
            generated_by="qaai_system",
            generated_at_iso="2026-01-01T00:00:00Z",
        ),
        artifacts=[],
        checksum="abc123",
    )

    seal = ExportSeal(
        algorithm="SHA256",
        digest="abc123",
        canonical_order=["metadata", "artifacts"],
    )

    pdf = PDFAuditExporter.export(
        audit_export=export,
        seal=seal,
    )

    assert "cryptographic_seal" in pdf
    assert pdf["cryptographic_seal"]["digest"] == "abc123"
