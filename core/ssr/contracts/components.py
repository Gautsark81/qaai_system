from dataclasses import dataclass


@dataclass(frozen=True)
class SSRComponentScore:
    """
    Atomic SSR component score.
    """
    name: str
    score: float          # 0.0 – 1.0
    weight: float
    metrics: dict[str, float]

    def __post_init__(self):
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("SSR component score must be in [0,1]")
