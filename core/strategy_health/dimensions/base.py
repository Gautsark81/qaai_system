from abc import ABC, abstractmethod
from typing import Iterable
from core.strategy_health.contracts.dimension import HealthDimensionScore


class DimensionEvaluator(ABC):
    """
    Base class for all health dimension evaluators.
    Evaluators must be PURE functions.
    """

    name: str

    @abstractmethod
    def evaluate(self, *, inputs: dict) -> HealthDimensionScore:
        """
        Compute a HealthDimensionScore from provided inputs.

        inputs is a dict to allow versioned expansion without
        breaking signatures.
        """
        raise NotImplementedError
