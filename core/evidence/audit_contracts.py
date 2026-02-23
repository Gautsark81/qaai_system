from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class AuditDecisionEntry:
    """
    Immutable, ordered view of a single decision for audit purposes.

    RULES:
    - Verbatim projection from DecisionEvidence
    - No inference
    - No enrichment
    - No mutation
    """
    decision_id: str
    decision_type: str
    timestamp: datetime

    strategy_id: Optional[str]
    parent_decision_id: Optional[str]

    # --- Governance (verbatim) ---
    governance_required: bool
    governance_status: Optional[str]
    reviewer: Optional[str]
    rationale: Optional[str]

    checksum: str


@dataclass(frozen=True)
class AuditSummary:
    start_time: datetime
    end_time: datetime
    total_decisions: int
    strategies_affected: int
    report_checksum: str


@dataclass(frozen=True)
class AuditSection:
    title: str
    description: str
    content: dict


@dataclass(frozen=True)
class AuditReport:
    """
    Auditor-grade, immutable replay report.

    Guarantees:
    - Deterministic
    - Read-only
    - Lineage-safe
    - Cryptographically checksummed
    """
    generated_at: datetime
    system_id: str

    # Ordered exactly as provided
    decisions: List[AuditDecisionEntry]

    summary: AuditSummary
    sections: List[AuditSection]

    methodology: str
    limitations: str

    # 🔒 Root-level checksum (canonical)
    checksum: str
