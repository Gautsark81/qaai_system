from core.compliance.audit_pack.builder import AuditPackBuilder
from core.compliance.incident_narrative.builder import IncidentNarrativeBuilder


def test_narrative_builds():
    pack = AuditPackBuilder().build()
    narrative = IncidentNarrativeBuilder().build(pack)

    assert narrative.summary
    assert len(narrative.sections) >= 3
