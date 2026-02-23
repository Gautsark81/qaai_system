# modules/meta/predict.py
from __future__ import annotations
from typing import Dict, Any, List
import numpy as np

from modules.meta.model import MetaModel, MetaModelError


def predict_from_vector(model: MetaModel, vector: List[float] | Any) -> Dict[str, float]:
    """
    Accepts a MetaModel instance and a feature vector (1D) and returns p_buy/p_sell/p_hold
    """
    if model is None:
        raise MetaModelError("Model is None")
    arr = np.atleast_2d(np.array(vector, dtype=float))
    return model.predict_proba(arr)
