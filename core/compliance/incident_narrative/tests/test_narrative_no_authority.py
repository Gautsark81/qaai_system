from core.compliance.audit_pack.builder import AuditPackBuilder
from core.compliance.incident_narrative.builder import IncidentNarrativeBuilder


def test_narrative_has_no_execution_authority():
    pack = AuditPackBuilder().build()
    narrative = IncidentNarrativeBuilder().build(pack)

    text = narrative.as_text().lower()
    assert "execute" not in text
    assert "place order" not in text
