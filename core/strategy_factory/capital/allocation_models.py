from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# Capital eligibility decision (C3.1)
# ============================================================

@dataclass(frozen=True)
class CapitalEligibilityDecision:
    eligible: bool
    reason: str


# ============================================================
# Capital allocation decision (C3.2)
# ============================================================

@dataclass(frozen=True)
class CapitalAllocationDecision:
    """
    Governance-only capital approval outcome.

    Canonical field: approved_capital
    Backward compatibility: allocated_capital (alias)
    """

    approved_capital: float
    reason: str

    # --------------------------------------------------------
    # Backward-compatibility constructor
    # --------------------------------------------------------
    def __init__(
        self,
        *,
        approved_capital: Optional[float] = None,
        allocated_capital: Optional[float] = None,
        reason: str,
    ):
        if approved_capital is None and allocated_capital is None:
            raise TypeError(
                "CapitalAllocationDecision requires "
                "`approved_capital` (preferred) or `allocated_capital` (legacy)"
            )

        value = (
            approved_capital
            if approved_capital is not None
            else allocated_capital
        )

        object.__setattr__(self, "approved_capital", float(value))
        object.__setattr__(self, "reason", reason)

    # --------------------------------------------------------
    # Legacy read-only alias
    # --------------------------------------------------------
    @property
    def allocated_capital(self) -> float:
        """
        Legacy alias. Read-only.
        """
        return self.approved_capital
