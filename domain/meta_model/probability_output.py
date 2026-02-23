from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ProbabilityOutput:
    """
    Read-only probability output.
    """
    p_up: float
    p_down: float
    confidence: float
    feature_importance: Dict[str, float]
    model_version: str
