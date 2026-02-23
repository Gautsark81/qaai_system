from dataclasses import dataclass


@dataclass(frozen=True)
class ChaosImpact:
    should_halt_trading: bool
    severity: str     # LOW / MEDIUM / HIGH / CRITICAL
