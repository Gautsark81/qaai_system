"""
StrategyEngine v1

Responsibilities:
- Provide a Strategy base class with lifecycle hooks.
- Implement SignalGenerator that uses a meta-model (LightGBM wrapper) to predict
  discrete signals: {-1,0,1} or probability/confidence if model exposes predict_proba.
- Provide a ModelAdapter to load the trained model (pickle ensemble from train_meta_model.py)
- Provide a lightweight orchestrator to convert model outputs -> (side, confidence, size) via sizing module.

Design goals:
- Minimal dependencies (pandas, numpy). Model loading expects the pickle saved by train_meta_model.py (ensemble wrapper).
- Test-friendly: pure functions, small methods.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, Callable
import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from strategy.sizing import kelly_position_size, volatility_target_size
from strategy.risk_filters import RiskConfig, check_risk_gates

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass
class Signal:
    symbol: str
    side: str        # "BUY" / "SELL" / "FLAT"
    confidence: float
    score: float     # model raw score (probability for up class)
    size: float      # suggested quantity (can be fractional; PortfolioEngine handles rounding)
    meta: Dict[str, Any]


class ModelAdapter:
    """
    Loads a pickled model saved by analytics/train_meta_model.py.
    Expected pickle content: dict with keys {'model': model-like, 'cv_aucs': [...]} or {'pipeline': pipe, 'cv_scores': [...]}

    The adapter exposes:
      - predict_proba(X_df) -> np.ndarray (n_samples, 2) with prob of class 1 (up) at [:,1]
      - predict(X_df) -> np.ndarray discrete classes (0,1,2)
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else None
        self.model = None
        if self.model_path:
            self.load(self.model_path)

    def load(self, path: Path) -> None:
        with open(path, "rb") as fh:
            obj = pickle.load(fh)
        # support both wrappers
        if isinstance(obj, dict) and "model" in obj:
            self.model = obj["model"]
        elif isinstance(obj, dict) and "pipeline" in obj:
            self.model = obj["pipeline"]
        else:
            # assume obj itself is a model
            self.model = obj
        logger.info("ModelAdapter: loaded model from %s", path)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not loaded")
        if hasattr(self.model, "predict_proba"):
            p = self.model.predict_proba(X)
            # Ensure shape (n,2)
            if p.ndim == 1:
                # some models return single-column proba -> wrap
                p = np.vstack([1 - p, p]).T
            return np.asarray(p)
        # fallback: use predict and map to one-hot-ish proba
        preds = self.model.predict(X)
        proba = np.zeros((len(preds), 2))
        # assume class '2' in earlier code mapped to up -> map 2 -> up
        # we map predicted classes to probability of "up" at column 1
        for i, v in enumerate(preds):
            if v in (1, 2):
                proba[i, 1] = 1.0
                proba[i, 0] = 0.0
            else:
                proba[i, 0] = 1.0
        return proba

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return np.asarray(self.model.predict(X))


class Strategy:
    """
    Base strategy class. Subclass and implement `generate` (state -> Signal).
    """

    def __init__(self, name: str, model_adapter: Optional[ModelAdapter] = None, risk_config: Optional[RiskConfig] = None):
        self.name = name
        self.model = model_adapter
        self.risk = risk_config or RiskConfig()

    def generate(self, symbol: str, features: pd.Series) -> Optional[Signal]:
        """
        Given symbol and a single-row features Series (feature-engine output), return a Signal or None.
        Subclasses may override, but the default behavior uses ModelAdapter -> size via sizing module.
        """
        if self.model is None:
            logger.debug("No model for strategy %s; no signal generated", self.name)
            return None

        X = features.to_frame().T  # keep column order
        proba = self.model.predict_proba(X)  # shape (1,2)
        p_up = float(proba[0, 1])
        p_down = float(proba[0, 0])
        score = p_up - p_down  # in [-1,1], positive -> buy
        confidence = abs(score)

        # Convert to discrete side
        if p_up > 0.55:
            side = "BUY"
        elif p_down > 0.55:
            side = "SELL"
        else:
            side = "FLAT"

        # compute sizing: try volatility targeting then kelly-lite as fallback
        volatility = float(features.get("atr_ratio", 0.0))
        try:
            size_vt = volatility_target_size(volatility=volatility, target_vol=0.02)
        except Exception:
            size_vt = 0.0
        try:
            kelly = kelly_position_size(edge=(p_up - p_down), win_prob=features.get("rolling_win_rate_20", 0.5) or 0.5, odds=1.0, max_fraction=0.05)
        except Exception:
            kelly = 0.0

        # blend sizes conservatively
        raw_size = float(max(size_vt, kelly)) * confidence

        # risk gates
        passed, reason = check_risk_gates(self.risk, symbol=symbol, proposed_size=raw_size, features=features)
        if not passed:
            logger.debug("Risk gate blocked signal for %s: %s", symbol, reason)
            return None

        sig = Signal(symbol=symbol, side=side, confidence=confidence, score=score, size=raw_size, meta={"p_up": p_up, "p_down": p_down})
        return sig


class StrategyEngine:
    """
    StrategyEngine orchestrates a set of strategies across a universe.

    Usage:
      engine = StrategyEngine([strategy_obj1, strategy_obj2])
      signals = engine.generate_signals(features_df)  # features_df indexed by (index) or multi-index; contains features + symbol column
    """

    def __init__(self, strategies: Optional[list] = None):
        self.strategies = strategies or []

    def register(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def generate_signals(self, features: pd.DataFrame) -> Dict[str, list]:
        """
        features: DataFrame with at least one row per (symbol). Expected columns include features used by model.
        Must contain either 'symbol' column or be multi-index where level name 'symbol' exists.

        Returns dict: strategy_name -> list[Signal]
        """
        out: Dict[str, list] = {}
        # normalize features mapping symbol -> row
        if "symbol" in features.columns:
            grouped = {s: g.iloc[-1] for s, g in features.groupby("symbol", sort=False)}
        elif "symbol" in features.index.names:
            # MultiIndex case
            idx = features.index
            if isinstance(idx, pd.MultiIndex):
                last_rows = features.groupby(level="symbol", sort=False).last()
                grouped = {s: last_rows.loc[s] for s in last_rows.index}
            else:
                raise ValueError("features index contains 'symbol' but grouping not possible")
        else:
            # assume features is per-symbol index
            # try to infer symbol from a column
            raise ValueError("features DataFrame must include a 'symbol' column or be MultiIndex with level 'symbol'")

        for strat in self.strategies:
            sigs = []
            for sym, row in grouped.items():
                try:
                    s = strat.generate(symbol=sym, features=row)
                    if s is not None:
                        sigs.append(s)
                except Exception:
                    logger.exception("Strategy %s failed for %s", strat.name, sym)
            out[strat.name] = sigs
        return out
