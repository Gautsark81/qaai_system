from __future__ import annotations
import numpy as np


class MetaModel:
    """
    Advisory meta-model.
    Outputs a confidence multiplier ∈ [0,1]
    """

    def score(self, features: dict) -> float:
        vol = features.get("volatility", 0.0)
        win_rate = features.get("win_rate", 0.5)

        score = 0.6 * win_rate + 0.4 * max(0.0, 1 - vol)
        return float(np.clip(score, 0.0, 1.0))
