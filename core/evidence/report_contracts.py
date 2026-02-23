# core/evidence/report_contracts.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


# ======================================================
# LEGACY-COMPATIBLE SUMMARY CONTRACT
# ======================================================

@dataclass(frozen=True)
class AuditReportSummary:
    """
    High-level summary for an audit / replay report.

    ⚠️ This contract is intentionally backward-compatible
    with legacy test expectations.
    """

    # Legacy fields (required by tests)
    decisions_total: int
    decisions_approved: int
    decisions_rejected: int

    # Modern extensions
    anomalies_detected: int
    notes: str


# 🔒 Backward compatibility alias
ReportSummary = AuditReportSummary


# ======================================================
# MASTER AUDIT REPORT
# ======================================================

@dataclass(frozen=True)
class ReplayAuditReport:
    """
    Auditor-grade immutable replay report.

    Guarantees:
    - Deterministic
    - Read-only
    - Hashable via checksum
    - Safe for regulator & investor export
    """

    generated_at: datetime
    from_timestamp: datetime
    to_timestamp: datetime

    evidence_count: int
    checksum: str

    # Summary is REQUIRED (explicit is safer than implicit)
    summary: AuditReportSummary

    frames_before: Dict[str, Any]
    frames_after: Dict[str, Any]
    diffs: Dict[str, Any]
