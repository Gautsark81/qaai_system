from dataclasses import dataclass
from .enums import DimensionVerdict


@dataclass(frozen=True)
class HealthDimensionScore:
    """
    Atomic health evaluation result for one dimension.
    """
    name: str
    score: float                  # 0.0 – 1.0
    weight: float                 # fixed per engine version
    metrics: dict[str, float]
    verdict: DimensionVerdict

    def __post_init__(self):
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Invalid score {self.score}; must be in [0.0, 1.0]")
