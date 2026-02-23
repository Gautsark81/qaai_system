from dataclasses import dataclass


@dataclass(frozen=True)
class PopulationConfig:
    max_population_per_symbol: int = 10
    min_fitness_threshold: float = 0.0
    max_age_steps: int = 500
    allow_warning: bool = True
