# modules/qnme/meta_controller.py
from typing import List, Dict, Any
import math
import logging

logger = logging.getLogger(__name__)

class MetaController:
    """
    Layer 4: Meta-Strategy Controller
    - Accepts validated signals and produces weighted portfolio-level actions
    - Applies smoothing, Bayesian updating and simple slippage forecast
    """

    def __init__(self, smoothing_tau: float = 5.0):
        self.smoothing_tau = max(1.0, float(smoothing_tau))
        self.last_weights: Dict[str, float] = {}
        self.regime_bias: Dict[str, float] = {}

    def set_regime_bias(self, bias_map: Dict[str, float]) -> None:
        """
        bias_map: {regime_name: global_multiplier}
        """
        self.regime_bias = bias_map

    def aggregate(self, validated_signals: List[Dict[str, Any]], regime: Dict[str, Any]) -> Dict[str, float]:
        """
        validated_signals: each element contains 'strategy_id', 'signal', 'confidence'
        returns: dict {strategy_id: smoothed_weight}
        """
        raw_scores = {}
        for v in validated_signals:
            sid = v["strategy_id"]
            conf = float(v.get("confidence", 0.5))
            raw_scores[sid] = max(raw_scores.get(sid, 0.0), conf)

        # apply regime multiplier
        regime_name = regime[0] if isinstance(regime, (list, tuple)) else regime.get("name", "")
        regime_mult = 1.0
        if regime_name and regime_name in self.regime_bias:
            regime_mult = self.regime_bias[regime_name]

        smoothed = {}
        for sid, score in raw_scores.items():
            last = self.last_weights.get(sid, 0.0)
            target = score * regime_mult
            smoothed_val = last + (target - last) / (1.0 + self.smoothing_tau)
            smoothed[sid] = smoothed_val
            self.last_weights[sid] = smoothed_val

        # normalize weights to sum <= 1.0 (simple)
        total = sum(abs(v) for v in smoothed.values()) or 1.0
        if total > 1.0:
            smoothed = {k: v / total for k, v in smoothed.items()}

        return smoothed

    def predict_slippage(self, tick: Dict[str, Any]) -> float:
        """
        Basic slippage forecast: larger spread and lower volume -> higher slippage
        """
        spread = tick.get("spread", 0.0)
        volume = tick.get("volume", 1.0)
        return float(min(1.0, (spread * 1000.0) / (volume + 1.0)))
