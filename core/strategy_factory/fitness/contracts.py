from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class FitnessInputs:
    sharpe: float
    win_rate: float
    max_drawdown: float
    trade_count: int
    regime_consistency: float
    tail_loss_ratio: float


@dataclass(frozen=True)
class FitnessResult:
    raw_fitness: float
    fragility_penalty: float
    is_capital_eligible: bool
    reasons: List[str] = ()

    @property
    def final_fitness(self) -> float:
        return round(max(0.0, self.raw_fitness - self.fragility_penalty), 4)


# ======================================================
# 🔁 BACKWARD-COMPAT / SEMANTIC ALIAS
# ======================================================

# CapitalFitness is intentionally an alias.
# CapitalAllocator and tests may use domain-specific naming.
CapitalFitness = FitnessResult
