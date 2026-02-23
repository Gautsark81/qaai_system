from dataclasses import dataclass


@dataclass(frozen=True)
class HealthFlag:
    """
    Human-readable explanation for health degradation.
    """
    code: str
    severity: str          # LOW | MEDIUM | HIGH
    message: str
    dimension: str
