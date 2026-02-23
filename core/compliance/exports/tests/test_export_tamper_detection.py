from core.compliance.exports.hasher import CanonicalSHA256Hasher
from core.compliance.exports.seal import seal_export, verify_export
from core.compliance.exports.contracts import AuditExport, ExportMetadata


def test_tampering_invalidates_checksum():
    hasher = CanonicalSHA256Hasher()

    export = AuditExport(
        metadata=ExportMetadata(
            export_version="1.0",
            export_type="AUDIT",
            generated_by="qaai_system",
            generated_at_iso="2026-01-01T00:00:00Z",
        ),
        artifacts=[{"a": 1}],
        checksum="",
    )

    seal = seal_export(export=export, hasher=hasher)

    sealed = AuditExport(
        metadata=export.metadata,
        artifacts=export.artifacts,
        checksum=seal.digest,
    )

    # Tamper with artifacts
    tampered = AuditExport(
        metadata=sealed.metadata,
        artifacts=[{"a": 999}],
        checksum=sealed.checksum,
    )

    assert verify_export(export=sealed, hasher=hasher) is True
    assert verify_export(export=tampered, hasher=hasher) is False
