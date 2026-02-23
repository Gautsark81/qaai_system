from core.compliance.audit_pack.builder import AuditPackBuilder


def test_checksum_detects_tampering():
    builder = AuditPackBuilder()
    pack = builder.build()

    tampered = pack.clone()
    tampered.manifest.version = "tampered"

    assert pack.checksum != tampered.compute_checksum()
