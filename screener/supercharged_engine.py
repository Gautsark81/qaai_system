from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd

from .features import FeatureExtractor
from .ml_model import LightweightClassifier
from .feedback import ScreenerFeedback
from qaai_system.utils.explainability import ExplainabilityLogger


class ScreeningEngineSupercharged:
    """
    Supercharged ensemble-style screening engine:
      - rule_score in [0..1] from rule-based heuristics
      - ml_score in [0..1] from lightweight classifier
      - feedback multiplier (>=0) adjusts final score
      - final_score = (w_rule * rule_score + w_ml * ml_score) * feedback
    """

    def __init__(
        self,
        w_rule: float = 0.5,
        w_ml: float = 0.5,
        feedback: Optional[ScreenerFeedback] = None,
        explain_logger: Optional[ExplainabilityLogger] = None,
    ):
        self.w_rule = float(w_rule)
        self.w_ml = float(w_ml)
        self.classifier = LightweightClassifier()
        self.feedback = feedback or ScreenerFeedback()
        self.explain = explain_logger or ExplainabilityLogger()

        # Buffers for online updates
        self._train_X: List[List[float]] = []
        self._train_y: List[int] = []
        self._symbols: List[str] = []

    # ----------------------------
    # Feature computation helpers
    # ----------------------------
    def _compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute all features using FeatureExtractor."""
        return FeatureExtractor.compute_all(df)

    def _compute_rule_score(self, row: pd.Series) -> float:
        """Simple heuristic rules → normalized score [0,1]."""
        parts = [
            float(row.get("rule_liquidity_ok", 0)),
            float(row.get("rule_low_volatility", 0)),
            float(row.get("rule_momentum_pos", 0)),
        ]
        return float(np.mean(parts))

    def _ml_score(self, row, ml_probs=None, i: int = None) -> float:
        """
        Compute ML score.
        - If ml_probs and i are given, return ml_probs[i].
        - Otherwise, compute directly from row features.
        """
        if ml_probs is not None and i is not None:
            return float(ml_probs[i]) if len(ml_probs) > i else 0.5

        feats = ["ADV20", "ATR14", "MOM10", "VOL10"]
        X = np.array([[row.get(f, 0) for f in feats]], dtype=float)
        return float(self.classifier.predict_proba(X)[0, 1])

    # ----------------------------
    # Training
    # ----------------------------
    def fit_classifier(self, df: pd.DataFrame, label_col: str = "label"):
        """
        Fit the classifier on a labeled dataset (1=good, 0=bad).
        """
        feats = ["ADV20", "ATR14", "MOM10", "VOL10"]
        X = df[feats].fillna(0).values
        y = df[label_col].astype(int).values
        if len(X) > 0:
            self.classifier.fit(X, y)

    # ----------------------------
    # Main screening pipeline
    # ----------------------------
    def screen(self, df: pd.DataFrame, top_k: int = 50) -> List[Tuple[str, float]]:
        """
        Run full screening on the most recent row per symbol.
        Returns top_k symbols with (symbol, score) sorted descending.
        """
        dfe = self._compute_features(df)
        latest = dfe.groupby("symbol").tail(1).reset_index(drop=True)

        results: List[Tuple[str, float]] = []

        # Prepare ML input
        feats = ["ADV20", "ATR14", "MOM10", "VOL10"]
        X = latest[feats].fillna(0).values
        ml_probs = (
            self.classifier.predict_proba(X)[:, 1]
            if len(X) > 0
            else np.zeros(len(latest))
        )

        for i, row in latest.iterrows():
            symbol = row["symbol"]
            rule_score = self._compute_rule_score(row)
            ml_score = self._ml_score(row, ml_probs, i)
            fb = self.feedback.get(symbol)
            final_score = (self.w_rule * rule_score + self.w_ml * ml_score) * fb

            # ✅ Flat structured log entry
            self.explain.log(
                symbol=symbol,
                timestamp=str(row.get("timestamp")),
                features={
                    "ADV20": row.get("ADV20"),
                    "ATR14": row.get("ATR14"),
                    "MOM10": row.get("MOM10"),
                    "VOL10": row.get("VOL10"),
                },
                score=final_score,
                reason="ensemble",
                rule_score=rule_score,
                ml_score=ml_score,
                feedback=fb,
                final_score=final_score,
            )

            results.append((symbol, float(final_score)))

        # Sort & return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # ----------------------------
    # Feedback integration
    # ----------------------------
    def add_feedback_example(self, symbol: str, features: List[float], label: int):
        """
        Store feedback for online training and refit periodically.
        """
        self._train_X.append(features)
        self._train_y.append(int(label))
        self._symbols.append(symbol)

        if len(self._train_y) >= 50:
            X = np.array(self._train_X)
            y = np.array(self._train_y)
            try:
                self.classifier.fit(X, y)
            except Exception:
                pass
            self._train_X.clear()
            self._train_y.clear()
            self._symbols.clear()

    # backward-compatibility alias (tests expect _rule_score)
    _rule_score = _compute_rule_score
