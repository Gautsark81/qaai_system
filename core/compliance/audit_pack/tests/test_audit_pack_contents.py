from core.compliance.audit_pack.builder import AuditPackBuilder


def test_audit_pack_contains_mandatory_sections():
    pack = AuditPackBuilder().build()

    keys = {artifact.kind for artifact in pack.artifacts}

    assert "SEBI_TRADE_EXPORT" in keys
    assert "CAPITAL_USAGE_LEDGER" in keys
    assert "GOVERNANCE_DECISIONS" in keys
    assert "LIFECYCLE_EVENTS" in keys
