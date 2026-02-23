from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .screening_governance_snapshot import ScreeningGovernanceSnapshot


@dataclass(frozen=True)
class CapitalContextAdvisory:
    """
    C5.10 — Capital Context Overlay (Advisory Only)

    HARD GUARANTEES:
    - Immutable
    - Deterministic
    - No capital mutation
    - No lifecycle mutation
    - No ranking mutation
    - No governance override
    """

    ranked_strategies: tuple[str, ...]
    base_state_hash: str
    capital_utilization_pct: Decimal
    adjusted_advisory_strength: Decimal


class CapitalContextOverlay:
    """
    Applies read-only capital context to advisory strength.
    """

    def apply(
        self,
        *,
        governance_snapshot: ScreeningGovernanceSnapshot,
        capital_utilization_pct: Decimal,
    ) -> CapitalContextAdvisory:

        # Clamp between 0 and 1 deterministically
        if capital_utilization_pct < Decimal("0"):
            capital_utilization_pct = Decimal("0")
        if capital_utilization_pct > Decimal("1"):
            capital_utilization_pct = Decimal("1")

        dampening = Decimal("1") - capital_utilization_pct

        adjusted_strength = (
            governance_snapshot.advisory_strength * dampening
        )

        return CapitalContextAdvisory(
            ranked_strategies=governance_snapshot.ranked_strategies,
            base_state_hash=governance_snapshot.state_hash,
            capital_utilization_pct=capital_utilization_pct,
            adjusted_advisory_strength=adjusted_strength,
        )