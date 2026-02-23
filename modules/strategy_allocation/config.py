from dataclasses import dataclass


@dataclass(frozen=True)
class AllocationConfig:
    min_health: float = 0.70
    max_drawdown: float = 0.08
    longevity_half_life: int = 200
    health_weight: float = 0.4
    fitness_weight: float = 0.4
    longevity_weight: float = 0.2
