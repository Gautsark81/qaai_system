# core/ml/advisory_engine.py

from datetime import date
from typing import List
from core.ml.feature_store import FeatureStore
from core.ml.model_registry import ModelRegistry
from core.ml.prediction_contract import MLPrediction
from core.observability.event_bus import EventBus


class AdvisoryEngine:
    """
    Orchestrates ML predictions.
    READ-ONLY intelligence.
    """

    def __init__(
        self,
        registry: ModelRegistry,
        feature_store: FeatureStore,
    ):
        self.registry = registry
        self.feature_store = feature_store

    def advise(
        self,
        model_name: str,
        entity_ids: List[str],
        trading_day: date,
    ) -> List[MLPrediction]:
        model = self.registry.get(model_name)
        predictions: List[MLPrediction] = []

        for entity_id in entity_ids:
            features = self.feature_store.load_features(
                entity_id, trading_day
            )

            prediction = model.predict(entity_id, features)
            predictions.append(prediction)

            # Observability only
            EventBus.emit(
                event_type="ML_SIGNAL",
                strategy_id=entity_id,
                payload={
                    "probability": prediction.probability,
                    "confidence": prediction.confidence,
                    "model_version": prediction.model_version,
                },
            )

        return predictions
