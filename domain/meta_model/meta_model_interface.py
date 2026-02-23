from abc import ABC, abstractmethod
from domain.meta_model.feature_contract import FeatureVector
from domain.meta_model.probability_output import ProbabilityOutput


class MetaModelInterface(ABC):
    """
    Deterministic, read-only meta-model interface.
    """

    @abstractmethod
    def infer(self, features: FeatureVector) -> ProbabilityOutput:
        ...
