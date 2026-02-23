# core/ml/prediction_contract.py

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MLPrediction:
    """
    Immutable advisory prediction.
    This object has NO executable authority.
    """
    entity_id: str              # strategy_id or symbol
    probability: float          # 0.0 → 1.0
    confidence: float           # model confidence
    horizon: str                # e.g. '1D', '5D'
    features_used: Dict[str, float]
    model_version: str
    advisory_note: str
