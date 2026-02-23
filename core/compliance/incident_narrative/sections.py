from typing import List
from core.compliance.audit_pack.models import AuditArtifact
from .models import NarrativeSection


def system_summary(artifacts: List[AuditArtifact]) -> NarrativeSection:
    return NarrativeSection(
        title="System Summary",
        content=(
            "This incident narrative was generated from a deterministic audit pack. "
            "All content is descriptive and contains no execution authority."
        ),
    )


def capital_section(artifacts: List[AuditArtifact]) -> NarrativeSection:
    ledger = next(
        a for a in artifacts if a.kind == "CAPITAL_USAGE_LEDGER"
    )
    entries = ledger.payload

    return NarrativeSection(
        title="Capital Usage",
        content=f"Total capital ledger entries observed: {len(entries)}.",
    )


def governance_section(artifacts: List[AuditArtifact]) -> NarrativeSection:
    gov = next(
        a for a in artifacts if a.kind == "GOVERNANCE_DECISIONS"
    )

    return NarrativeSection(
        title="Governance Decisions",
        content=f"Governance metadata present: {sorted(gov.payload.keys())}.",
    )


def lifecycle_section(artifacts: List[AuditArtifact]) -> NarrativeSection:
    lifecycle = next(
        a for a in artifacts if a.kind == "LIFECYCLE_EVENTS"
    )

    return NarrativeSection(
        title="Lifecycle Events",
        content=f"Lifecycle events captured: {len(lifecycle.payload)}.",
    )
