# core/oversight/correlation/engine.py

from datetime import datetime
from typing import Iterable, Optional, Set, Tuple

from core.oversight.contracts.correlated_event import CorrelatedOversightEvent
from core.oversight.contracts.finding import OversightFinding


_SEVERITY_ORDER = {
    "INFO": 0,
    "WARNING": 1,
    "CRITICAL": 2,
}


def correlate_findings(
    *,
    event_id: str,
    generated_at: datetime,
    findings: Iterable[OversightFinding],
    min_distinct_domains: int = 2,
) -> Optional[CorrelatedOversightEvent]:
    """
    Pure correlation engine.

    Combines multiple oversight findings into a single
    correlated oversight event.

    Returns None if correlation threshold is not met.
    """

    findings = tuple(findings)

    if not findings:
        return None

    domains: Set[str] = {f.domain for f in findings}
    detectors: Set[str] = {f.detector for f in findings}

    if len(domains) < min_distinct_domains:
        return None

    # --- severity escalation ---
    max_severity = max(
        findings,
        key=lambda f: _SEVERITY_ORDER[f.severity],
    ).severity

    evidence_ids: Tuple[str, ...] = tuple(
        f.evidence_id for f in findings if f.evidence_id
    )

    contributing_findings = tuple(
        f.summary for f in findings
    )

    return CorrelatedOversightEvent(
        event_id=event_id,
        generated_at=generated_at,
        severity=max_severity,
        involved_domains=frozenset(domains),
        detectors=frozenset(detectors),
        summary="Correlated oversight risk detected",
        contributing_findings=contributing_findings,
        evidence_ids=evidence_ids,
        requires_human_attention=(max_severity != "INFO"),
    )
