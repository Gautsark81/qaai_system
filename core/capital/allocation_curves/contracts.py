from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalCurveSnapshot:
    eligible: bool
    allocation_pct: float
    reason: str
    version: str

    def __post_init__(self):
        if not (0.0 <= self.allocation_pct <= 1.0):
            raise ValueError("allocation_pct must be in [0,1]")
