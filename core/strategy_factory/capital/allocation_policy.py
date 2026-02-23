from __future__ import annotations

from core.strategy_factory.capital.models import CapitalEligibilityDecision
from core.strategy_factory.capital.allocation_models import CapitalAllocationDecision


def apply_allocation_policy(
    *,
    eligibility: CapitalEligibilityDecision,
    requested_capital: float,
    max_per_strategy: float,
    global_cap_remaining: float,
) -> CapitalAllocationDecision:
    """
    Apply capital allocation policy limits.

    Governance-only:
    - No execution
    - No broker logic
    - No side effects
    - Deterministic
    """

    # --------------------------------------------------
    # 1️⃣ Ineligible strategies receive zero capital
    # --------------------------------------------------
    if not eligibility.eligible:
        return CapitalAllocationDecision(
            approved_capital=0,
            reason=f"Allocation denied: {eligibility.reason}",
        )

    # --------------------------------------------------
    # 2️⃣ Enforce per-strategy cap
    # --------------------------------------------------
    approved = min(requested_capital, max_per_strategy)

    if approved < requested_capital:
        return CapitalAllocationDecision(
            approved_capital=approved,
            reason="Allocation capped by max per strategy",
        )

    # --------------------------------------------------
    # 3️⃣ Enforce global remaining capital
    # --------------------------------------------------
    approved = min(approved, global_cap_remaining)

    if approved < requested_capital:
        return CapitalAllocationDecision(
            approved_capital=approved,
            reason="Allocation capped by global cap remaining",
        )

    # --------------------------------------------------
    # ✅ Full approval
    # --------------------------------------------------
    return CapitalAllocationDecision(
        approved_capital=approved,
        reason="Allocation approved within policy limits",
    )
