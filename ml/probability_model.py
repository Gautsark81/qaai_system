# path: qaai_system/ml/probability_model.py
from __future__ import annotations

"""
Lightweight probability model for signals.

This is NOT a real ML model, but a deterministic, feature-based scoring
layer that behaves like one:

Inputs (if present in the signal DataFrame):
- edge
- signal_strength
- zscore

Outputs:
- win_prob  (0..1)
- ml_confidence (0..1)

If no relevant features are present, we fall back to 0.5 / 0.5.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


def _logistic(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


@dataclass
class ProbabilityModelConfig:
    """
    Config for the probability model.

    scale: how aggressively to scale raw features into logits.
    """

    edge_scale: float = 1.0
    strength_scale: float = 0.7
    zscore_scale: float = 0.5


class ProbabilityModel:
    def __init__(self, config: Optional[ProbabilityModelConfig] = None) -> None:
        self.config = config or ProbabilityModelConfig()

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add win_prob and ml_confidence columns to a copy of df.

        Heuristics:
        - Use 'edge' if present, else 'signal_strength', else 'zscore'.
        - Apply logistic transform.
        - ml_confidence ~ distance from 0.5.
        """
        if df.empty:
            return df

        df = df.copy()

        edge = df.get("edge")
        strength = df.get("signal_strength")
        zscore = df.get("zscore")

        raw = np.zeros(len(df), dtype=float)

        if edge is not None:
            raw = raw + edge.fillna(0.0).to_numpy(dtype=float) * self.config.edge_scale
        elif strength is not None:
            raw = raw + strength.fillna(0.0).to_numpy(dtype=float) * self.config.strength_scale
        elif zscore is not None:
            raw = raw + zscore.fillna(0.0).to_numpy(dtype=float) * self.config.zscore_scale

        win_prob = _logistic(raw)
        ml_confidence = 0.5 + np.abs(win_prob - 0.5)  # [0.5, 1.0]

        df["win_prob"] = win_prob.clip(0.0, 1.0)
        df["ml_confidence"] = ml_confidence.clip(0.0, 1.0)

        return df
