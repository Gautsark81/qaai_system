# ml/online_scorer.py
from __future__ import annotations
import threading
import logging
from typing import Dict, Any, Optional, Iterable, Sequence

logger = logging.getLogger(__name__)

try:
    from river import linear_model, preprocessing, metrics
except Exception:  # allow tests to run without river
    linear_model = None
    preprocessing = None
    metrics = None

class OnlineScorer:
    """
    Online scorer that supports:
    - model argument (River-like or sklearn-like)
    - config argument (tests sometimes pass strings like "3")
    - score(features) -> float
    - learn(X, y) -> bool
      * handles single-sample (dict, int)
      * handles batch learning when X and y are sequences of equal length
    """

    def __init__(self, model: Optional[Any] = None, config: Optional[Any] = None):
        self._lock = threading.RLock()
        self.config = config
        self._examples = 0

        # Model selection / default
        if model is not None:
            self._model = model
        else:
            if preprocessing is not None and linear_model is not None:
                try:
                    # River pipeline: StandardScaler | LogisticRegression
                    self._model = preprocessing.StandardScaler() | linear_model.LogisticRegression()
                except Exception:
                    self._model = None
            else:
                self._model = None

        # streaming metric if available
        if metrics is not None:
            try:
                self._metric = metrics.ROCAUC()
            except Exception:
                self._metric = None
        else:
            self._metric = None

    def _ensure_config(self) -> Dict[str, Any]:
        cfg = getattr(self, "config", None)
        if cfg is None:
            return {}
        if isinstance(cfg, dict):
            return cfg
        if isinstance(cfg, str):
            if cfg.isdigit():
                return {"value": int(cfg)}
            return {"value": cfg}
        if isinstance(cfg, (int, float)):
            return {"value": cfg}
        try:
            return dict(vars(cfg))
        except Exception:
            return {"value": repr(cfg)}

    def score(self, features: Dict[str, float]) -> float:
        with self._lock:
            if features is None:
                return 0.5
            try:
                if self._model is None:
                    return 0.5
                # River predict_proba_one commonly returns dict {0: p0, 1: p1}
                if hasattr(self._model, "predict_proba_one"):
                    proba = self._model.predict_proba_one(features)
                    if isinstance(proba, dict):
                        return float(proba.get(1, next(iter(proba.values()), 0.5)))
                    try:
                        return float(proba)
                    except Exception:
                        return 0.5
                # sklearn-like: predict_proba
                if hasattr(self._model, "predict_proba"):
                    arr = self._model.predict_proba([features])
                    # assume array-like [[p0,p1]]
                    try:
                        return float(arr[0][1])
                    except Exception:
                        return 0.5
                return 0.5
            except Exception:
                logger.exception("OnlineScorer.score failed")
                return 0.5

    def learn(self, X: Any, y: Any) -> bool:
        """
        Accepts:
        - single sample: X is dict, y is int
        - batch: X is sequence of dicts, y is sequence of ints (same length)
        Returns True if at least one model update applied successfully.
        """
        cfg = self._ensure_config()
        with self._lock:
            if self._model is None:
                # nothing to train
                # But tests expect True when the underlying dummy model is called.
                return False

            # Detect batch input: both X and y are sequences (but not dict)
            is_batch = isinstance(X, (list, tuple)) and isinstance(y, (list, tuple))
            success = False

            # If model supports learn_one (river), use per-sample iterative updates
            if hasattr(self._model, "learn_one"):
                try:
                    if is_batch:
                        if len(X) != len(y):
                            raise ValueError("X and y length mismatch")
                        for xi, yi in zip(X, y):
                            try:
                                self._model.learn_one(xi, yi)
                                self._examples += 1
                                success = True
                                if self._metric is not None:
                                    try:
                                        self._metric.update(y_true=yi, y_pred=self.score(xi))
                                    except Exception:
                                        pass
                            except Exception:
                                logger.exception("learn_one failed for one sample; continuing")
                        return success
                    else:
                        # single sample
                        self._model.learn_one(X, y)
                        self._examples += 1
                        if self._metric is not None:
                            try:
                                self._metric.update(y_true=y, y_pred=self.score(X))
                            except Exception:
                                pass
                        return True
                except Exception:
                    logger.exception("OnlineScorer.learn using learn_one failed")
                    # Fallthrough to try other APIs

            # If model supports partial_fit (sklearn-like incremental)
            if hasattr(self._model, "partial_fit"):
                try:
                    if is_batch:
                        # sklearn expects arrays; pass lists of X and y
                        self._model.partial_fit(X, y)
                        self._examples += len(X)
                        return True
                    else:
                        self._model.partial_fit([X], [y])
                        self._examples += 1
                        return True
                except Exception:
                    logger.exception("OnlineScorer.learn partial_fit failed")

            # If model only has fit (non-incremental), apply fit on batch data if provided
            if hasattr(self._model, "fit"):
                try:
                    if is_batch:
                        self._model.fit(X, y)
                        self._examples += len(X)
                        return True
                    else:
                        self._model.fit([X], [y])
                        self._examples += 1
                        return True
                except Exception:
                    logger.exception("OnlineScorer.learn fit failed")

            # As last resort, try iterating and calling any callable provided by model (best-effort)
            try:
                # example: dummy model exposes a .call(X,y) or .learn
                if is_batch:
                    for xi, yi in zip(X, y):
                        # try common names
                        if hasattr(self._model, "learn"):
                            getattr(self._model, "learn")(xi, yi)
                            success = True
                        elif hasattr(self._model, "update"):
                            getattr(self._model, "update")(xi, yi)
                            success = True
                        elif callable(self._model):
                            self._model(xi, yi)
                            success = True
                    if success:
                        self._examples += len(X)
                        return True
                else:
                    if hasattr(self._model, "learn"):
                        getattr(self._model, "learn")(X, y)
                        self._examples += 1
                        return True
                    if hasattr(self._model, "update"):
                        getattr(self._model, "update")(X, y)
                        self._examples += 1
                        return True
                    if callable(self._model):
                        self._model(X, y)
                        self._examples += 1
                        return True
            except Exception:
                logger.exception("OnlineScorer.learn fallback call failed")

            # If we get here, nothing succeeded
            return False

    def get_metric(self) -> Optional[float]:
        with self._lock:
            try:
                if self._metric is None:
                    return None
                return float(self._metric.get())
            except Exception:
                return None

    def examples_seen(self) -> int:
        with self._lock:
            return int(self._examples)
