import hashlib
from domain.meta_model.meta_model_interface import MetaModelInterface
from domain.meta_model.feature_contract import FeatureVector
from domain.meta_model.probability_output import ProbabilityOutput


class ReferenceMetaModel(MetaModelInterface):
    """
    Deterministic reference model.
    """

    MODEL_VERSION = "ref-1.0"

    def infer(self, features: FeatureVector) -> ProbabilityOutput:
        # Deterministic hash-based pseudo-probability
        seed = (
            features.window_id
            + features.schema_version
            + "".join(sorted(features.values.keys()))
        )
        h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        p_up = (h % 1000) / 1000.0
        p_down = 1.0 - p_up

        return ProbabilityOutput(
            p_up=p_up,
            p_down=p_down,
            confidence=abs(p_up - 0.5) * 2,
            feature_importance={k: 1.0 / len(features.values) for k in features.values},
            model_version=self.MODEL_VERSION,
        )
