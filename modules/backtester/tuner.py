from __future__ import annotations
import math
import numpy as np
import pandas as pd

try:
    import optuna  # optional
except Exception:  # pragma: no cover
    optuna = None

from qaai_system.signal_engine.signal_engine_supercharged import (
    SignalEngineSupercharged,
)


class StrategyTuner:
    """
    Hyperparameter tuner for indicator windows / thresholds.
    Uses Optuna if available; otherwise falls back to a simple random search.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.se = SignalEngineSupercharged()

    def _score(self, rsi_window: int, atr_window: int) -> float:
        df = self.data.copy()
        df["RSI"] = self.se.rsi(df["close"], window=rsi_window)
        df["ATR"] = self.se.atr(df, window=atr_window)

        # Example: simple PnL proxy
        signals = np.where(df["RSI"] < 30, 1, np.where(df["RSI"] > 70, -1, 0))

        # ✅ FIX: replace deprecated fillna(method="ffill") with .ffill()
        ret = np.diff(df["close"].ffill(), prepend=df["close"].iloc[0])

        pnl = float(np.sum(signals * ret))

        # Regularization penalty to avoid extreme params
        reg = -0.01 * (abs(rsi_window - 14) + abs(atr_window - 14))
        return pnl + reg

    # -------- Optuna path --------
    def _optuna_objective(self, trial):
        rsi_window = trial.suggest_int("rsi_window", 5, 30)
        atr_window = trial.suggest_int("atr_window", 5, 30)
        return self._score(rsi_window, atr_window)

    def run(self, n_trials: int = 25) -> dict:
        if optuna is not None:
            study = optuna.create_study(direction="maximize")
            study.optimize(self._optuna_objective, n_trials=n_trials)
            return study.best_params

        # -------- Fallback random search (no Optuna) --------
        rng = np.random.default_rng(42)
        best = (-math.inf, {"rsi_window": 14, "atr_window": 14})

        for _ in range(n_trials):
            rsi_w = int(rng.integers(5, 31))
            atr_w = int(rng.integers(5, 31))
            score = self._score(rsi_w, atr_w)
            if score > best[0]:
                best = (score, {"rsi_window": rsi_w, "atr_window": atr_w})

        return best[1]
