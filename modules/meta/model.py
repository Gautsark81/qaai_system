# modules/meta/model.py
from __future__ import annotations
import os
from typing import Tuple, Any, Dict
import numpy as np

# scikit-learn optional
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

try:
    import joblib
except Exception:
    joblib = None


class MetaModelError(RuntimeError):
    pass


class MetaModel:
    """
    Simple meta-model wrapper around sklearn.RandomForestClassifier producing
    probabilities for classes ['buy', 'sell', 'hold'] mapped to labels (1, -1, 0).
    - save(path)
    - load(path)
    - fit(X, y)
    - predict_proba(X) -> dict with p_buy, p_sell, p_hold
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        if not SKLEARN_AVAILABLE:
            raise MetaModelError("scikit-learn not available. Install scikit-learn to use MetaModel.")
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        self.label_map = {1: "buy", -1: "sell", 0: "hold"}

    def fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Fit model and return simple metrics dict. y expected to be {1,-1,0}.
        """
        if not SKLEARN_AVAILABLE:
            raise MetaModelError("sklearn not available")

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_val)
        acc = float(accuracy_score(y_val, preds))
        return {"accuracy": acc, "n_samples": len(y)}

    def predict_proba(self, X: np.ndarray) -> Dict[str, float]:
        """
        Return aggregated probabilities p_buy, p_sell, p_hold.
        X can be 1D (single sample) or 2D (n_samples, n_features).
        For a single sample, returns dict of floats; for multiple returns list[dict].
        """
        if not SKLEARN_AVAILABLE:
            raise MetaModelError("sklearn not available")
        X_arr = np.atleast_2d(X)
        probs = self.model.predict_proba(X_arr)  # shape (n, n_classes)
        # sklearn's classes_ returns mapping of index to label value (e.g., [-1,0,1])
        classes = list(self.model.classes_)
        out = []
        for row in probs:
            d = {}
            for idx, cls in enumerate(classes):
                label = self.label_map.get(cls, str(cls))
                d[f"p_{label}"] = float(row[idx])
            out.append(d)
        if len(out) == 1:
            return out[0]
        return out

    def save(self, path: str) -> None:
        if joblib is None:
            raise MetaModelError("joblib is required for persistence. Install joblib.")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        joblib.dump(self.model, path)

    def load(self, path: str) -> None:
        if joblib is None:
            raise MetaModelError("joblib is required for persistence. Install joblib.")
        self.model = joblib.load(path)
