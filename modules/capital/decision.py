from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalDecision:
    """
    Phase 13.2 – Advisory Capital Decision

    HARD INVARIANTS:
    - scale_factor ∈ [0, 1]
    - max_notional ≤ requested_notional
    - NEVER overrides RiskManager
    - NEVER increases exposure
    """

    approved: bool
    max_notional: float
    scale_factor: float
    reason: str

    def is_scaling_only(self) -> bool:
        """
        Contract guard used by tests and allocators.
        """
        return 0.0 <= self.scale_factor <= 1.0
