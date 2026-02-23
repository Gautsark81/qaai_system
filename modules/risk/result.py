# modules/risk/result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    allowed: bool
    quantity: int | None
    reason: str
