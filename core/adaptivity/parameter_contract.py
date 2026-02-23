# core/adaptivity/parameter_contract.py

from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveParameter:
    """
    Immutable definition of a tunable parameter.
    """
    name: str
    current_value: float
    min_value: float
    max_value: float
    description: str

    def validate(self, new_value: float):
        if not (self.min_value <= new_value <= self.max_value):
            raise RuntimeError(
                f"Parameter {self.name} out of bounds: "
                f"{new_value} not in [{self.min_value}, {self.max_value}]"
            )
