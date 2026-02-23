from core.compliance.audit_pack.builder import AuditPackBuilder
from core.compliance.incident_narrative.builder import IncidentNarrativeBuilder


def test_narrative_contains_expected_sections():
    pack = AuditPackBuilder().build()
    narrative = IncidentNarrativeBuilder().build(pack)

    titles = [s.title for s in narrative.sections]

    assert "Capital Usage" in titles
    assert "Governance Decisions" in titles
    assert "Lifecycle Events" in titles
