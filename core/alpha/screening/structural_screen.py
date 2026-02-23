# core/alpha/screening/structural_screen.py

from typing import List

from .structural_evidence import StructuralRiskEvidence
from .structural_verdict import StructuralRiskVerdict


EVENT_BLOCKERS = {
    "binary_event_dependency",
    "litigation_risk",
    "delisting_risk",
    "merger_uncertainty",
}

BALANCE_SHEET_BLOCKERS = {
    "excessive_leverage",
    "negative_operating_cashflow",
    "refinancing_dependency",
    "going_concern_risk",
}

REGULATORY_BLOCKERS = {
    "policy_dependency",
    "license_concentration",
    "price_control_exposure",
    "compliance_binary_risk",
}


def run_structural_risk_screen(
    *,
    symbol: str,
    evidence: StructuralRiskEvidence,
) -> StructuralRiskVerdict:
    blocked: List[str] = []
    reasons: List[str] = []

    # 1. Event risk
    if any(flag in EVENT_BLOCKERS for flag in evidence.event_risk_flags):
        blocked.append("event_risk")
        reasons.append("Blocked due to structural event risk")

    # 2. Balance sheet fragility
    if any(flag in BALANCE_SHEET_BLOCKERS for flag in evidence.balance_sheet_flags):
        blocked.append("balance_sheet")
        reasons.append("Blocked due to balance sheet fragility")

    # 3. Regulatory sensitivity
    if any(flag in REGULATORY_BLOCKERS for flag in evidence.regulatory_flags):
        blocked.append("regulatory")
        reasons.append("Blocked due to regulatory sensitivity")

    if blocked:
        return StructuralRiskVerdict(
            passed=False,
            reasons=tuple(reasons),
            blocked_dimensions=tuple(blocked),
        )

    return StructuralRiskVerdict(
        passed=True,
        reasons=("Structural risk screening passed",),
        blocked_dimensions=(),
    )
