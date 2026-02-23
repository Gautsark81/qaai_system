from dataclasses import dataclass
from typing import Literal


def _clip(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


AgeBucket = Literal["early", "mid", "late"]


@dataclass(frozen=True)
class GlobalRegimeState:
    regime_label: str
    start_cycle: int
    current_cycle: int
    duration_cycles: int
    age_bucket: AgeBucket
    transition_score: float
    stability_score: float
    structural_break_score: float
    confidence_score: float

    def __post_init__(self):
        object.__setattr__(self, "transition_score", _clip(self.transition_score))
        object.__setattr__(self, "stability_score", _clip(self.stability_score))
        object.__setattr__(self, "structural_break_score", _clip(self.structural_break_score))
        object.__setattr__(self, "confidence_score", _clip(self.confidence_score))


@dataclass(frozen=True)
class PortfolioRegimeState:
    portfolio_id: str
    derived_from_global_label: str
    duration_cycles: int
    age_bucket: AgeBucket
    portfolio_transition_score: float
    portfolio_stability_score: float
    portfolio_break_score: float
    portfolio_confidence_score: float

    def __post_init__(self):
        object.__setattr__(self, "portfolio_transition_score", _clip(self.portfolio_transition_score))
        object.__setattr__(self, "portfolio_stability_score", _clip(self.portfolio_stability_score))
        object.__setattr__(self, "portfolio_break_score", _clip(self.portfolio_break_score))
        object.__setattr__(self, "portfolio_confidence_score", _clip(self.portfolio_confidence_score))