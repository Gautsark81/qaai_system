# core/ml/feature_store.py

from typing import Dict
from datetime import date


class FeatureStore:
    """
    Read-only feature access layer.
    ML cannot mutate data.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, float]] = {}

    def load_features(
        self,
        entity_id: str,
        trading_day: date,
    ) -> Dict[str, float]:
        """
        Deterministic feature retrieval.
        """
        key = f"{entity_id}:{trading_day}"
        return self._cache.get(key, {})

    def preload(
        self,
        entity_id: str,
        trading_day: date,
        features: Dict[str, float],
    ):
        """
        Explicit preload only.
        Used by offline pipelines.
        """
        key = f"{entity_id}:{trading_day}"
        self._cache[key] = features.copy()
