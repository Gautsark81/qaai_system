from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScreeningEvidence:
    """
    Atomic, structured evidence used to justify
    screening decisions.
    """

    metric: str
    value: float
    threshold: Optional[float]
    interpretation: str

    def to_dict(self) -> dict:
        return {
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "interpretation": self.interpretation,
        }
