from core.compliance.audit_pack.builder import AuditPackBuilder


def test_audit_pack_is_deterministic():
    builder = AuditPackBuilder()

    pack1 = builder.build()
    pack2 = builder.build()

    assert pack1.serialize() == pack2.serialize()
    assert pack1.checksum == pack2.checksum
