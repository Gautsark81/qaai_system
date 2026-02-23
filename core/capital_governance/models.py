from dataclasses import dataclass
from typing import Dict, Tuple


# =========================
# PHASE 32.1 — POSTURE
# =========================

@dataclass(frozen=True)
class StrategyCapitalView:
    strategy_id: str
    allocated_capital: float
    utilized_capital: float
    drawdown: float


@dataclass(frozen=True)
class PortfolioCapitalPosture:
    total_allocated: float
    total_utilized: float
    max_drawdown: float
    per_strategy: Dict[str, StrategyCapitalView]


# =========================
# PHASE 32.2 — CORRELATION & CONCENTRATION
# =========================

@dataclass(frozen=True)
class CorrelationWarning:
    strategy_a: str
    strategy_b: str
    correlation: float
    threshold: float


@dataclass(frozen=True)
class ConcentrationWarning:
    strategy_id: str
    allocated_capital: float
    portfolio_fraction: float
    threshold: float


@dataclass(frozen=True)
class CapitalCorrelationConcentrationView:
    correlations: Tuple[CorrelationWarning, ...]
    concentrations: Tuple[ConcentrationWarning, ...]


# =========================
# PHASE 32.3 — STRESS
# =========================

@dataclass(frozen=True)
class StrategyStressContribution:
    strategy_id: str
    worst_case_loss: float
    scenario: str


@dataclass(frozen=True)
class PortfolioStressEnvelope:
    total_worst_case_loss: float
    per_strategy: Tuple[StrategyStressContribution, ...]
    scenario_count: int
