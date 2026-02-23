# qaai_system/analytics/meta_model.py
from __future__ import annotations
import logging
import math
import random
from dataclasses import dataclass
from typing import Optional

# model loading
from pathlib import Path

# 🔒 Authoritative environment
from env_validator import CONFIG

IS_LIVE = CONFIG.mode == "live"

logger = logging.getLogger(__name__)

_MODEL_PATH = Path("models/meta_model.joblib")
_SKLEARN_PATH = Path("models/meta_model.pkl")  # alternate
_LGB_PATH = Path("models/meta_model.txt")  # LightGBM raw booster (optional)


# Lightweight Feature dataclass used across registry/promotion engine
@dataclass
class MetaModelFeatures:
    strategy_id: str
    version: str
    symbol: str
    win_rate: float
    profit_factor: float
    net_pnl: float
    # optional extras
    volatility_regime: str | None = None
    mcap_bucket: str | None = None


# Wrapper class
class StrategyMetaModel:
    def __init__(self) -> None:
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        # Try joblib sklearn first
        try:
            if _MODEL_PATH.exists():
                import joblib
                self.model = joblib.load(_MODEL_PATH)
                logger.info("Loaded meta model from %s", _MODEL_PATH)
                return
        except Exception:
            if IS_LIVE:
                raise RuntimeError("Failed to load sklearn joblib model in LIVE mode.")
            logger.exception("Failed to load sklearn joblib model")

        # Optionally try pickle
        try:
            if _SKLEARN_PATH.exists():
                import joblib
                self.model = joblib.load(_SKLEARN_PATH)
                logger.info("Loaded meta model from %s", _SKLEARN_PATH)
                return
        except Exception:
            if IS_LIVE:
                raise RuntimeError("Failed to load sklearn pickle model in LIVE mode.")
            logger.exception("Failed to load sklearn pickle model")

        # fallback: no model found
        if IS_LIVE:
            raise RuntimeError("No trained meta-model found in LIVE mode.")
        logger.info("No trained meta-model found; using heuristic fallback")

    def score(self, f: MetaModelFeatures) -> float:
        """
        If a trained model is present, compute features -> model.predict_proba -> score.
        Otherwise, use a stable heuristic:
            score = win_rate * log1p(profit_factor) * (1 + small net_pnl factor)
        """

        if self.model is not None:
            try:
                # Build numeric vector in same order as trainer (win_rate, profit_factor, net_pnl)
                vec = [float(f.win_rate), float(f.profit_factor), float(f.net_pnl)]

                # model may be sklearn or LGBM wrapper; handle predict_proba / predict
                if hasattr(self.model, "predict_proba"):
                    p = self.model.predict_proba([vec])
                    if p.shape[1] >= 2:
                        return float(p[0, 1])
                    else:
                        return float(p[0, 0])
                else:
                    v = float(self.model.predict([vec])[0])
                    return 1.0 / (1.0 + math.exp(-v / (abs(v) + 1e-6)))

            except Exception:
                if IS_LIVE:
                    raise RuntimeError("Model scoring failed in LIVE mode.")
                logger.exception("Model scoring failed; falling back to heuristic")

        # --------------------------------------------------
        # Deterministic heuristic fallback
        # --------------------------------------------------

        wr = float(f.win_rate or 0.0)
        pf = float(max(0.0, f.profit_factor or 0.0))
        net = float(f.net_pnl or 0.0)

        base = wr * math.log1p(max(pf, 0.0))

        if net > 0:
            base *= 1.02

        # 🔒 Institutional Rule:
        # No randomness in LIVE.
        # Determinism must be guaranteed.
        if IS_LIVE:
            return base

        # Non-live environments may retain minor jitter for experimentation
        return base + random.uniform(-0.01, 0.01)