from datetime import datetime, timezone
from typing import List, Optional

from core.evidence.audit_contracts import (
    AuditReport,
    AuditSection,
    AuditSummary,
    AuditDecisionEntry,
)
from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.checksum import compute_checksum


def generate_audit_report_json(
    *,
    system_id: str,
    evidence: List[DecisionEvidence],
    generated_at: Optional[datetime] = None,
) -> AuditReport:
    """
    Generate a deterministic, auditor-grade audit report.

    Invariants:
    - Evidence is NEVER mutated
    - Ordering is preserved exactly
    - Governance metadata is surfaced verbatim
    - No enrichment or inference
    - Checksum is governance-sensitive
    - Timestamp is deterministic unless explicitly injected
    """

    if not evidence:
        raise ValueError("Audit report requires at least one evidence record")

    # ------------------------------------------------------------------
    # 🔒 Deterministic timestamp resolution
    #
    # IMPORTANT:
    # - NEVER call the clock implicitly
    # - If not injected, fall back to a stable, timezone-aware epoch
    # ------------------------------------------------------------------
    if generated_at is None:
        generated_at = datetime.fromtimestamp(0, tz=timezone.utc)

    # --- Ordered, immutable projection ---
    decisions = [
        AuditDecisionEntry(
            decision_id=e.decision_id,
            decision_type=e.decision_type,
            timestamp=e.timestamp,
            strategy_id=e.strategy_id,
            parent_decision_id=e.parent_decision_id,

            # Governance (verbatim)
            governance_required=e.governance_required,
            governance_status=e.governance_status,
            reviewer=e.reviewer,
            rationale=e.rationale,

            # Source decision checksum
            checksum=e.checksum,
        )
        for e in evidence
    ]

    start_time = decisions[0].timestamp
    end_time = decisions[-1].timestamp

    strategies = {
        d.strategy_id for d in decisions if d.strategy_id is not None
    }

    # ------------------------------------------------------------------
    # 🔒 Deterministic, governance-sensitive audit checksum
    #
    # NOTE:
    # compute_checksum expects an iterable of (key, value) pairs.
    # We therefore FLATTEN each decision deterministically.
    # ------------------------------------------------------------------

    checksum_fields = []

    for idx, d in enumerate(decisions):
        prefix = f"decision[{idx}]"

        checksum_fields.extend([
            (f"{prefix}.decision_id", d.decision_id),
            (f"{prefix}.decision_type", d.decision_type),
            (f"{prefix}.timestamp", d.timestamp.isoformat()),
            (f"{prefix}.strategy_id", d.strategy_id),
            (f"{prefix}.parent_decision_id", d.parent_decision_id),

            # Governance fields (must affect checksum)
            (f"{prefix}.governance_required", d.governance_required),
            (f"{prefix}.governance_status", d.governance_status),
            (f"{prefix}.reviewer", d.reviewer),
            (f"{prefix}.rationale", d.rationale),

            # Underlying decision integrity
            (f"{prefix}.decision_checksum", d.checksum),
        ])

    report_checksum = compute_checksum(fields=checksum_fields)

    summary = AuditSummary(
        start_time=start_time,
        end_time=end_time,
        total_decisions=len(decisions),
        strategies_affected=len(strategies),
        report_checksum=report_checksum,
    )

    sections = [
        AuditSection(
            title="Decision Timeline",
            description="Ordered sequence of recorded decisions",
            content={
                "events": [
                    {
                        "decision_id": d.decision_id,
                        "timestamp": d.timestamp.isoformat(),
                        "decision_type": d.decision_type,
                        "strategy_id": d.strategy_id,
                        "parent_decision_id": d.parent_decision_id,
                        "governance_required": d.governance_required,
                        "governance_status": d.governance_status,
                        "reviewer": d.reviewer,
                        "rationale": d.rationale,
                        "checksum": d.checksum,
                    }
                    for d in decisions
                ]
            },
        ),
        AuditSection(
            title="Reproducibility Statement",
            description="Deterministic replay guarantee",
            content={
                "deterministic": True,
                "ordering": "caller-provided",
                "side_effects": "none",
            },
        ),
    ]

    return AuditReport(
        generated_at=generated_at,
        system_id=system_id,
        decisions=decisions,
        summary=summary,
        sections=sections,
        methodology=(
            "Audit report generated from append-only DecisionEvidence. "
            "Ordering is preserved exactly as provided."
        ),
        limitations=(
            "Report reflects recorded decisions only. "
            "Market data and execution outcomes are out of scope."
        ),
        # ✅ Canonical, governance-sensitive checksum
        checksum=report_checksum,
    )
