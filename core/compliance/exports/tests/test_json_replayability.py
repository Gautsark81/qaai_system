from core.compliance.exports.json_export import JSONAuditExporter
from core.compliance.exports.contracts import AuditExport, ExportMetadata, ExportSeal

def test_json_export_is_replay_safe():
    export = AuditExport(
        metadata=ExportMetadata(
            export_version="1.0",
            export_type="AUDIT",
            generated_by="qaai_system",
            generated_at_iso="2026-01-01T00:00:00Z",
        ),
        artifacts=[{"event": "TEST"}],
        checksum="hash123",
    )

    seal = ExportSeal(
        algorithm="SHA256",
        digest="hash123",
        canonical_order=["metadata", "artifacts"],
    )

    json_payload = JSONAuditExporter.export(
        audit_export=export,
        seal=seal,
    )

    assert isinstance(json_payload, dict)
    assert "metadata" in json_payload
    assert "artifacts" in json_payload
    assert "seal" in json_payload
