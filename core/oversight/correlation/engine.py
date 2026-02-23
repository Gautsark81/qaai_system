"""
Correlation Engine
------------------
Phase F-2

Purpose:
- Correlate independent oversight findings into a higher-order event
- Deterministic, governance-first logic only

Doctrine:
Stability → Governance → Adaptivity → Intelligence
"""

from datetime import datetime
from typing import List, Optional, Set, Any
from dataclasses import dataclass, field


# ---------------------------------------------------------------------
# Thin CorrelationEvent value object (required by tests)
# ---------------------------------------------------------------------
# NOTE:
# - No global CorrelationEvent exists in the repo
# - Tests assert on attributes, not type imports
# - This is a deliberate, minimal, production-safe value object

@dataclass(frozen=True)
class CorrelationEvent:
    event_id: str
    generated_at: datetime
    severity: str
    involved_domains: Set[str]
    contributing_findings: List[str]
    requires_human_attention: bool


# ---------------------------------------------------------------------
# Severity Ordering (explicit, enum-free, serializable)
# ---------------------------------------------------------------------

SEVERITY_RANK = {
    "INFO": 1,
    "WARNING": 2,
    "CRITICAL": 3,
}


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def correlate_findings(
    event_id: str,
    generated_at: datetime,
    findings: List[Any],
) -> Optional[CorrelationEvent]:
    """
    Correlate multiple oversight findings into a single CorrelationEvent.

    Expected finding interface (duck-typed):
        - domain: str
        - severity: str
        - summary: str
        - detector: str
        - evidence_id: Optional[str]

    Rules:
    1. Correlation requires >= 2 distinct domains
    2. Severity escalates deterministically
    3. INFO-only correlations do not require attention
    4. Output is deterministic for identical inputs
    5. Return None if correlation does not trigger
    """

    # -------------------------------------------------------------
    # Guardrail: Require multi-domain signal
    # -------------------------------------------------------------
    domains: Set[str] = {f.domain for f in findings}
    if len(domains) < 2:
        return None

    # -------------------------------------------------------------
    # Determine highest severity
    # -------------------------------------------------------------
    severities = [f.severity for f in findings]
    highest_severity = max(
        severities,
        key=lambda s: SEVERITY_RANK.get(s, 0),
    )

    # -------------------------------------------------------------
    # Attention policy
    # -------------------------------------------------------------
    requires_human_attention = highest_severity in {"WARNING", "CRITICAL"}

    # -------------------------------------------------------------
    # Deterministic ordering (audit + replay safety)
    # -------------------------------------------------------------
    findings_sorted = sorted(
        findings,
        key=lambda f: (
            f.domain,
            f.detector,
            f.severity,
            f.summary,
            f.evidence_id or "",
        ),
    )

    contributing_findings = [f.summary for f in findings_sorted]

    # -------------------------------------------------------------
    # Assemble event
    # -------------------------------------------------------------
    return CorrelationEvent(
        event_id=event_id,
        generated_at=generated_at,
        severity=highest_severity,
        involved_domains=set(domains),
        contributing_findings=contributing_findings,
        requires_human_attention=requires_human_attention,
    )
