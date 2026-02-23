from dataclasses import dataclass


@dataclass(frozen=True)
class MetaAlphaAllocation:
    """
    Advisory-only capital allocation recommendation.
    Immutable, deterministic, and explainable.
    """
    strategy_id: str
    recommended_weight: float
    rationale: str
