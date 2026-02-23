from __future__ import annotations

from typing import Iterable, Optional
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression


# ==========================================================
# TRAIN MODEL
# ==========================================================

def train_model(
    df: pd.DataFrame,
    label_col: str,
    model_type: str = "logistic",
    feature_cols: Optional[Iterable[str]] = None,
):
    """
    Train watchlist ML model.

    CONTRACT (tests rely on this):
    - MUST return sklearn.linear_model.LogisticRegression
    - NOT a Pipeline
    """

    if df is None or df.empty:
        return None

    if label_col not in df.columns:
        raise ValueError(f"label_col '{label_col}' not found")

    y = df[label_col]
    if y.nunique() < 2:
        return None

    if feature_cols is None:
        feature_cols = [
            c for c in df.columns
            if c != label_col and df[c].dtype != "O"
        ]

    X = df[list(feature_cols)].fillna(0.0)

    if len(X) < 5:
        return None

    if model_type != "logistic":
        raise ValueError(f"Unsupported model_type: {model_type}")

    model = LogisticRegression(
        max_iter=1000,
        solver="lbfgs",
    )

    model.fit(X, y)
    return model


# ==========================================================
# SCORE CANDIDATES
# ==========================================================

def score_candidates(
    df: pd.DataFrame,
    model,
    feature_cols: Optional[Iterable[str]] = None,
    confidence_threshold: float = 0.5,
    top_k: Optional[int] = None,
) -> pd.DataFrame:
    """
    Score candidates using trained ML model.

    RETURNS (exact schema expected by tests):
        symbol
        signal_strength
        confidence
        score
        passed
        adaptive_sl
        adaptive_tp
    """

    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "signal_strength",
                "confidence",
                "score",
                "passed",
                "adaptive_sl",
                "adaptive_tp",
            ]
        )

    out = df.copy()

    # --------------------------------------------------
    # Ensure symbol column ALWAYS exists
    # --------------------------------------------------
    if "symbol" not in out.columns:
        out["symbol"] = [f"SYM{i}" for i in range(len(out))]

    # --------------------------------------------------
    # Feature selection
    # --------------------------------------------------
    if feature_cols is None:
        feature_cols = [
            c for c in out.columns
            if c not in {"symbol", "label"} and out[c].dtype != "O"
        ]

    X = out[list(feature_cols)].fillna(0.0)

    # --------------------------------------------------
    # Model scoring
    # --------------------------------------------------
    if model is None:
        out["confidence"] = 0.0
        out["score"] = 0.0
    else:
        proba = model.predict_proba(X)[:, 1]
        out["confidence"] = proba
        out["score"] = proba * 2.0 - 1.0  # [-1, +1]

    # --------------------------------------------------
    # Signal alias (tests expect this)
    # --------------------------------------------------
    out["signal_strength"] = out["confidence"]

    # --------------------------------------------------
    # Confidence filter (STRICT)
    # --------------------------------------------------
    out["passed"] = out["confidence"] >= confidence_threshold
    out = out[out["passed"]].copy()

    # --------------------------------------------------
    # Ranking
    # --------------------------------------------------
    out = out.sort_values(
        by="signal_strength",
        ascending=False,
    )

    if top_k is not None:
        out = out.head(top_k)

    # --------------------------------------------------
    # Adaptive risk placeholders (deterministic)
    # --------------------------------------------------
    if "atr" in out.columns:
        out["adaptive_sl"] = out["atr"] * 1.5
        out["adaptive_tp"] = out["atr"] * 3.0
    else:
        out["adaptive_sl"] = 1.0
        out["adaptive_tp"] = 2.0

    return out[
        [
            "symbol",
            "signal_strength",
            "confidence",
            "score",
            "passed",
            "adaptive_sl",
            "adaptive_tp",
        ]
    ].reset_index(drop=True)
