# qaai_system/analytics/model_monitor.py
from __future__ import annotations
import logging, json
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)
MODEL_DIR = Path("models")
MODEL_FILE = MODEL_DIR / "meta_model.joblib"
DRIFT_LOG = Path("data/monitor/drift_log.jsonl")
DRIFT_LOG.parent.mkdir(parents=True, exist_ok=True)

def load_model():
    if not MODEL_FILE.exists():
        logger.warning("No model file found: %s", MODEL_FILE)
        return None
    return joblib.load(MODEL_FILE)

def compute_feature_importance(booster_wrapped) -> Dict[str, float]:
    """
    Expect wrapper has .boosters or .booster; try to extract feature importance.
    """
    fi = {}
    # If ensemble wrapper with boosters
    boosters = getattr(booster_wrapped, "boosters", None) or getattr(booster_wrapped, "boosters", None)
    if boosters is None and hasattr(booster_wrapped, "booster"):
        boosters = [booster_wrapped.booster]
    if boosters is None and hasattr(booster_wrapped, "booster_"):
        boosters = [booster_wrapped.booster_]
    if boosters is None:
        # unknown format; cannot compute importance
        logger.warning("Unknown model format for feature importance")
        return fi
    # average importance across boosters
    importances = []
    for b in boosters:
        try:
            # LightGBM booster
            fmap = b.feature_importance(importance_type="gain")
            # b.feature_name() may exist
            names = getattr(b, "feature_name", lambda: None)()
            if names is None:
                names = [f"f{i}" for i in range(len(fmap))]
            imp = dict(zip(names, fmap))
            importances.append(imp)
        except Exception:
            logger.exception("Failed to extract booster importance")
    # merge
    if importances:
        all_names = sorted(set().union(*[set(d.keys()) for d in importances]))
        avg = {}
        for n in all_names:
            vals = [d.get(n, 0.0) for d in importances]
            avg[n] = float(np.mean(vals))
        return avg
    return fi

def log_drift_if_needed(current_importance: Dict[str, float], baseline_importance: Dict[str, float], threshold: float = 0.5):
    """
    Very simple drift detection: if top-K features shift by more than `threshold`
    fraction of total importance compared to baseline, write an alert.
    """
    # compute top features in baseline and current
    def top_features(d, k=3):
        items = sorted(d.items(), key=lambda x: x[1], reverse=True)
        return [x[0] for x in items[:k]]
    if not baseline_importance:
        baseline_importance = {}
    current_top = top_features(current_importance, k=3)
    baseline_top = top_features(baseline_importance, k=3)
    # measure Jaccard similarity
    set_cur = set(current_top); set_base = set(baseline_top)
    inter = len(set_cur.intersection(set_base))
    union = len(set_cur.union(set_base)) or 1
    jaccard = inter / union
    if jaccard < (1 - threshold):
        # log alert
        alert = {"ts": pd.Timestamp.utcnow().isoformat(), "type":"feature_drift", "current_top": current_top, "baseline_top": baseline_top, "jaccard": jaccard}
        with DRIFT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(alert) + "\n")
        logger.warning("Feature drift detected: jaccard=%.3f; alert logged", jaccard)
        return alert
    return None

def run_monitor(baseline_path: Path | None = None):
    model = load_model()
    if model is None:
        logger.warning("No model to monitor")
        return
    current_imp = compute_feature_importance(model) or {}
    baseline_imp = {}
    if baseline_path and baseline_path.exists():
        try:
            baseline_imp = json.loads(baseline_path.read_text(encoding="utf-8"))
        except Exception:
            baseline_imp = {}
    alert = log_drift_if_needed(current_imp, baseline_imp, threshold=0.5)
    # persist current importance as next baseline optionally
    (MODEL_DIR / "last_feature_importance.json").write_text(json.dumps(current_imp), encoding="utf-8")
    return {"current": current_imp, "baseline": baseline_imp, "alert": alert}
