from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.strategy_factory.capital.governance_models import (
    CapitalGovernanceDecision,
    CapitalGovernanceLimits,
)


# ============================================================
# Governance Audit Model (minimal for wiring)
# ============================================================

@dataclass(frozen=True)
class CapitalGovernanceAudit:
    strategy_dna: str
    decision: CapitalGovernanceDecision
    requested_capital: float
    limits: CapitalGovernanceLimits
    created_at: datetime
    fingerprint: str


# ============================================================
# Audit Builder (PURE, DETERMINISTIC)
# ============================================================

def build_capital_governance_audit(
    *,
    strategy_dna: str,
    decision: CapitalGovernanceDecision,
    limits: CapitalGovernanceLimits,
    requested_capital: float,
    created_at: datetime,
) -> CapitalGovernanceAudit:
    """
    Minimal governance audit builder.

    NOTE:
    - Deterministic
    - No hashing yet (C4.1-B will harden this)
    - Exists only to unblock C4 wiring
    """

    fingerprint = (
        f"{strategy_dna}|{decision.allowed}|{requested_capital}|"
        f"{limits.global_cap}|{limits.max_per_strategy}|{limits.max_concentration_pct}"
    )

    return CapitalGovernanceAudit(
        strategy_dna=strategy_dna,
        decision=decision,
        requested_capital=requested_capital,
        limits=limits,
        created_at=created_at,
        fingerprint=fingerprint,
    )
