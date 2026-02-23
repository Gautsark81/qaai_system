from __future__ import annotations
import numpy as np

# Try sklearn but gracefully fall back to a simple linear model
try:
    from sklearn.linear_model import LogisticRegression

    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


class LightweightClassifier:
    """
    Wraps either sklearn LogisticRegression (if available) or a
    deterministic fallback that computes a weighted linear score.
    """

    def __init__(self):
        if SKLEARN_AVAILABLE:
            self.model = LogisticRegression(max_iter=200)
            self._is_trained = False
        else:
            # fallback uses simple weights updated by .fit() storing means
            self.model = None
            self._is_trained = False
            self._weights = None
            self._bias = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        if SKLEARN_AVAILABLE:
            self.model.fit(X, y)
            self._is_trained = True
        else:
            # simple pseudo-fit: compute per-feature correlation with label
            if X.size == 0:
                self._weights = np.zeros((X.shape[1],))
                self._bias = 0.0
            else:
                corr = np.array(
                    [
                        np.corrcoef(X[:, i], y)[0, 1] if np.std(X[:, i]) > 0 else 0.0
                        for i in range(X.shape[1])
                    ]
                )
                corr = np.nan_to_num(corr)
                # normalize
                norm = np.linalg.norm(corr)
                self._weights = corr / (norm + 1e-9)
                self._bias = float(np.mean(y) * 0.0)
            self._is_trained = True

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self._is_trained:
            # uniform 0.5 if not trained
            return np.vstack([0.5 * np.ones(X.shape[0]), 0.5 * np.ones(X.shape[0])]).T
        if SKLEARN_AVAILABLE:
            return self.model.predict_proba(X)
        # fallback: sigmoid(weights.dot(x) + bias)
        scores = X.dot(self._weights) + self._bias
        probs = 1.0 / (1.0 + np.exp(-scores))
        return np.vstack([1 - probs, probs]).T
