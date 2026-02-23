from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
from core.regime.taxonomy import MarketRegime


# ======================================================
# 🧠 STRATEGY CAPITAL PROFILE
# ======================================================

@dataclass(frozen=True)
class StrategyCapitalProfile:
    strategy_id: str
    max_allocation: float
    min_fitness: float


# ======================================================
# 🚦 DECISION STATUS
# ======================================================

class CapitalDecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    THROTTLED = "THROTTLED"
    BLOCKED = "BLOCKED"


# ======================================================
# 📊 ALLOCATION VALUE
# ======================================================

@dataclass(frozen=True)
class AllocationValue:
    allocated_fraction: float

    def __eq__(self, other):
        """
        Allows test comparisons like:
        AllocationValue(0.3) == 0.3
        """
        if isinstance(other, (int, float)):
            return self.allocated_fraction == other
        return False


# ======================================================
# 🧾 STRATEGY DECISION
# ======================================================

@dataclass(frozen=True)
class StrategyDecision:
    """
    Final per-strategy decision snapshot.

    This object is:
    - Deterministic
    - Serializable
    - Safe for evidence & replay
    """

    strategy_id: str
    raw_fitness: float
    fragility_penalty: float
    final_allocation: float
    regime: MarketRegime
    reasons: List[str]
    is_capital_eligible: bool


# ======================================================
# 🧾 CAPITAL ATTRIBUTION (EXPLANATORY, ADDITIVE)
# ======================================================

@dataclass(frozen=True)
class CapitalAttribution:
    """
    Capital attribution is EXPLANATORY, not prescriptive.

    Design invariants:
    - Must never affect allocation math
    - Must be constructible even for blocked strategies
    - Must be deterministic and auditable
    """

    strategy_id: str
    final_allocation: float
    applied_constraints: List[str] = field(default_factory=list)

    # ---- Optional explanatory fields (safe defaults) ----
    raw_fitness: float = 0.0
    fragility_penalty: float = 0.0
    regime_throttle: float = 1.0
    final_weight: float = 0.0


# ======================================================
# 📦 CAPITAL DECISION ARTIFACT
# ======================================================

@dataclass(frozen=True)
class CapitalDecisionArtifact:
    """
    Canonical capital allocation decision artifact.

    Properties:
    - Pure data (no behavior)
    - Fully replayable
    - Evidence-safe
    """

    allocations: Dict[str, AllocationValue]
    decisions: Dict[str, StrategyDecision]
    attribution: Dict[str, CapitalAttribution]
    total_allocated: float
    status: CapitalDecisionStatus
