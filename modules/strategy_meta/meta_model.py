from typing import Dict, List, Tuple
import math

from modules.strategy_meta.training_sample import MetaTrainingSample


class MetaModel:
    """
    Advisory meta-model.

    Uses a simple, explainable weighted distance model.
    Deterministic and safe by design.
    """

    def __init__(self, feature_weights: Dict[str, float]):
        self.feature_weights = feature_weights
        self._centroids: Dict[Tuple[str, str], Dict[str, float]] = {}
        self._trained = False

    # --------------------------------------------------
    # TRAINING (OFFLINE)
    # --------------------------------------------------

    def train(self, samples: List[MetaTrainingSample]) -> None:
        """
        Learns centroids per (strategy_id, regime).
        """
        buckets: Dict[Tuple[str, str], List[Dict[str, float]]] = {}

        for s in samples:
            key = (s.strategy_id, s.regime)
            buckets.setdefault(key, []).append(s.features)

        self._centroids = {
            key: self._mean_features(fs)
            for key, fs in buckets.items()
        }
        self._trained = True

    # --------------------------------------------------
    # INFERENCE (READ-ONLY)
    # --------------------------------------------------

    def score(
        self,
        *,
        strategy_id: str,
        regime: str,
        context_features: Dict[str, float],
    ) -> float:
        """
        Returns compatibility score ∈ [0, 1].
        """
        if not self._trained:
            return 0.0

        centroid = self._centroids.get((strategy_id, regime))
        if not centroid:
            return 0.0

        dist = self._weighted_distance(centroid, context_features)
        return round(1.0 / (1.0 + dist), 4)

    # --------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------

    def explain(
        self,
        *,
        strategy_id: str,
        regime: str,
        context_features: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Per-feature contribution to distance.
        """
        centroid = self._centroids.get((strategy_id, regime))
        if not centroid:
            return {}

        return {
            k: abs(centroid.get(k, 0.0) - context_features.get(k, 0.0))
            * self.feature_weights.get(k, 1.0)
            for k in centroid.keys()
        }

    # --------------------------------------------------
    # INTERNALS
    # --------------------------------------------------

    def _mean_features(self, features: List[Dict[str, float]]) -> Dict[str, float]:
        keys = features[0].keys()
        return {
            k: sum(f[k] for f in features) / len(features)
            for k in keys
        }

    def _weighted_distance(
        self,
        a: Dict[str, float],
        b: Dict[str, float],
    ) -> float:
        s = 0.0
        for k, w in self.feature_weights.items():
            s += w * (a.get(k, 0.0) - b.get(k, 0.0)) ** 2
        return math.sqrt(s)
