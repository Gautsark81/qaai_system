from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class CapitalStressReport:
    """
    Portfolio-level stress result (existing, unchanged).
    """
    shock_name: str
    pre_shock_weights: Dict[str, float]
    post_shock_weights: Dict[str, float]
    max_weight_pre: float
    max_weight_post: float


# -------------------------------------------------
# Advisory-only per-strategy stress surface (NEW)
# -------------------------------------------------

@dataclass(frozen=True)
class StressReport:
    """
    Advisory stress signal for a single strategy.
    No execution authority.
    No capital mutation.
    """
    strategy_id: str
    worst_case_loss: float
    scenario: str
