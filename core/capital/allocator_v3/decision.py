from dataclasses import dataclass
from typing import Dict, List, Optional

from .contracts import (
    AllocationValue,
    CapitalAttribution,
    CapitalDecisionArtifact,
    CapitalDecisionStatus,
    StrategyDecision,
)


# ======================================================
# 🧾 DECISION WRAPPER / HELPERS
# ======================================================

def empty_decision(reason: str) -> CapitalDecisionArtifact:
    """
    Create a BLOCKED capital decision artifact.

    Used when capital allocation is prevented
    before allocator logic runs (kill-switch, system guard, etc.)

    Design rules:
    - Deterministic
    - No allocations
    - Safe for evidence emission
    """

    return CapitalDecisionArtifact(
        allocations={},
        decisions={},
        attribution={},
        total_allocated=0.0,
        status=CapitalDecisionStatus.BLOCKED,
    )


# ======================================================
# 🔎 LEGACY / ADAPTER VIEW (NON-BREAKING)
# ======================================================

@dataclass(frozen=True)
class CapitalDecisionView:
    """
    Lightweight / legacy-compatible view over CapitalDecisionArtifact.

    Exists ONLY for backward compatibility with older tests
    and components that expect:
      - allocations: Dict[str, float]
      - reasons: Dict[str, list]

    This class MUST NOT affect allocator semantics.
    """

    allocations: Dict[str, float]
    reasons: Dict[str, List[str]]
    attribution: Optional[Dict[str, CapitalAttribution]] = None

    @classmethod
    def from_artifact(
        cls,
        artifact: CapitalDecisionArtifact,
    ) -> "CapitalDecisionView":
        """
        Adapt a full decision artifact into a legacy-safe view.
        """

        return cls(
            allocations={
                strategy_id: allocation.allocated_fraction
                for strategy_id, allocation in artifact.allocations.items()
            },
            reasons={
                strategy_id: decision.reasons
                for strategy_id, decision in artifact.decisions.items()
            },
            attribution=artifact.attribution,
        )


# ======================================================
# 🛡️ OPTIONAL SAFE ACCESSORS (ADDITIVE)
# ======================================================

def decision_is_blocked(artifact: CapitalDecisionArtifact) -> bool:
    """
    Convenience helper — does NOT replace status checks.
    """
    return artifact.status == CapitalDecisionStatus.BLOCKED


def decision_total_allocation(artifact: CapitalDecisionArtifact) -> float:
    """
    Explicit accessor for deterministic reads.
    """
    return artifact.total_allocated
