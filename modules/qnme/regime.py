# modules/qnme/regime.py
from typing import Dict, Tuple, Optional, Sequence, Any
import math

# 16 example micro-regimes — canonical names
MICRO_REGIMES = [
    "low_vol_range", "low_vol_grind", "high_vol_trend", "macro_trend",
    "high_vol_fakeout", "liquidity_vacuum", "reversal_heavy", "structural_breakout",
    "momentum_exhaustion", "sideways_compression", "distribution", "accumulation",
    "microstructural_drift", "breakout_with_failure", "range_shift_pretrend", "terminal_trend_exhaustion"
]


class RegimeEngine:
    """
    Layer 1: Market Regime Engine
    - Lightweight rule-based fallback that returns (regime_name, confidence)
    - Can be replaced with a trained classifier (sklearn, xgboost, etc.)
    """

    def __init__(self, classifier: Optional[Any] = None):
        # classifier should implement predict_proba(X) and classes_
        self.classifier = classifier

    def predict(self, genome: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predict the regime label and confidence.
        If classifier is None, use simple heuristics.
        """
        if self.classifier is None:
            return self._rule_based(genome)
        try:
            vec = self._flatten(genome)
            probs = self.classifier.predict_proba([vec])[0]
            idx = int(max(range(len(probs)), key=lambda i: probs[i]))
            return str(self.classifier.classes_[idx]), float(probs[idx])
        except Exception:
            return self._rule_based(genome)

    def _flatten(self, genome: Dict[str, Any]) -> Sequence[float]:
        g = genome.get("genome", {})
        return [g.get(k, 0.0) for k in ("entropy", "avg_dt", "volume", "imbalance", "liquidity_p_large")]

    def _rule_based(self, genome: Dict[str, Any]) -> Tuple[str, float]:
        g = genome.get("genome", {})
        ent = g.get("entropy", 0.0)
        vol = g.get("volume", 0.0)
        imbalance = g.get("imbalance", 0.0)
        # simple heuristics to map to a regime
        if vol > 10000 and ent > 4.5:
            return "high_vol_trend", 0.85
        if abs(imbalance) > 100:
            return "liquidity_vacuum", 0.75
        if ent < 1.0 and vol < 2000:
            return "low_vol_range", 0.7
        return "sideways_compression", 0.5
