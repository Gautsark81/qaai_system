from core.compliance.audit_pack.builder import AuditPackBuilder
from core.compliance.incident_narrative.builder import IncidentNarrativeBuilder


def test_narrative_is_deterministic():
    pack = AuditPackBuilder().build()
    builder = IncidentNarrativeBuilder()

    n1 = builder.build(pack).as_text()
    n2 = builder.build(pack).as_text()

    assert n1 == n2
