# core/ml/meta_model.py

from typing import Dict
from core.ml.prediction_contract import MLPrediction


class MetaModel:
    """
    Abstract advisory ML meta-model.
    """

    def __init__(self, version: str):
        self.version = version

    def predict(
        self,
        entity_id: str,
        features: Dict[str, float],
    ) -> MLPrediction:
        """
        Override in concrete implementations.
        """
        raise NotImplementedError
