from domain.meta_model.meta_model_interface import MetaModelInterface
from domain.meta_model.feature_contract import FeatureVector
from domain.meta_model.probability_output import ProbabilityOutput
from domain.meta_model.read_only_guard import ReadOnlyGuard


class MetaModelContextAdapter:
    """
    Supplies probabilistic context to strategies.
    """

    def __init__(self, model: MetaModelInterface):
        self.model = model

    def get_context(self, features: FeatureVector) -> ProbabilityOutput:
        out = self.model.infer(features)
        ReadOnlyGuard.assert_read_only(out)
        return out
