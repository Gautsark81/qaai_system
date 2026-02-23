from core.compliance.audit_pack.models import AuditPack
from .models import IncidentNarrative
from .sections import (
    system_summary,
    capital_section,
    governance_section,
    lifecycle_section,
)


class IncidentNarrativeBuilder:
    """
    Deterministic, read-only narrative generator.

    RULES:
    - Must not mutate state
    - Must not execute logic
    - Must derive solely from AuditPack
    """

    def build(self, pack: AuditPack) -> IncidentNarrative:
        artifacts = pack.artifacts

        sections = [
            system_summary(artifacts),
            capital_section(artifacts),
            governance_section(artifacts),
            lifecycle_section(artifacts),
        ]

        return IncidentNarrative(
            summary="Incident Narrative Report",
            sections=sections,
        )
