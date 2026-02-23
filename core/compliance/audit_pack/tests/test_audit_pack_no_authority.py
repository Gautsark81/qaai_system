from core.compliance.audit_pack.builder import AuditPackBuilder


def test_audit_pack_has_no_execution_authority():
    pack = AuditPackBuilder().build()

    for artifact in pack.artifacts:
        assert not hasattr(artifact, "execute")
        assert not hasattr(artifact, "mutate")
        assert not hasattr(artifact, "submit")
