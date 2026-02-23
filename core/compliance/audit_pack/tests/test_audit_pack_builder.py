from core.compliance.audit_pack.builder import AuditPackBuilder
from core.compliance.audit_pack.models import AuditPack


def test_audit_pack_builds_successfully():
    builder = AuditPackBuilder()

    pack = builder.build()

    assert isinstance(pack, AuditPack)
    assert pack.manifest is not None
    assert pack.checksum is not None
    assert len(pack.artifacts) > 0
