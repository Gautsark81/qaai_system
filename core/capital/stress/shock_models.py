from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalShock:
    """
    Deterministic capital shock scenario.
    """
    name: str
    multiplier: float   # Applied to strategy weights
