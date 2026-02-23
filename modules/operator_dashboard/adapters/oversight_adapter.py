from typing import List

from core.oversight.contracts.finding import OversightFinding

from modules.operator_dashboard.contracts.oversight import (
    OversightEventSnapshot,
)


def get_oversight_event_snapshots() -> List[OversightEventSnapshot]:
    """
    Read-only adapter between core oversight and operator dashboard.

    Phase-F guarantees:
    - NO mutation
    - NO orchestration
    - NO assumptions about runtime wiring
    - Safe if oversight is not yet globally exposed
    """

    # -------------------------------------------------
    # Oversight is optional at this layer.
    # If no global collector exists, degrade gracefully.
    # -------------------------------------------------
    try:
        from core.oversight.runtime import collect_oversight_findings  # optional
        findings: List[OversightFinding] = collect_oversight_findings()
    except Exception:
        return []

    snapshots: List[OversightEventSnapshot] = []

    for f in findings:
        snapshots.append(
            OversightEventSnapshot(
                domain=f.domain,
                severity=f.severity,
                summary=f.summary,
                detector=f.detector,
                evidence_id=f.evidence_id,
            )
        )

    # Deterministic ordering for snapshot equality
    return sorted(
        snapshots,
        key=lambda s: (s.severity, s.domain, s.detector),
    )
