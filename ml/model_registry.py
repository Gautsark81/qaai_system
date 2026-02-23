# ml/model_registry.py
from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Dict, Any
import joblib

REGISTRY_DIR_DEFAULT = "ml_models"

class ModelRegistry:
    """
    Simple file-system model registry: stores model file and metadata JSON.
    Methods:
      - save_model(model_obj, name, metadata) -> path
      - load_model(name, version=None) -> (model, metadata)
      - list_models() -> list metadata
    """

    def __init__(self, registry_dir: str = REGISTRY_DIR_DEFAULT):
        self._root = registry_dir
        os.makedirs(self._root, exist_ok=True)

    def _meta_path(self, name: str):
        return os.path.join(self._root, f"{name}.meta.json")

    def _model_path(self, name: str, timestamp: str):
        return os.path.join(self._root, f"{name}__{timestamp}.pkl")

    def save_model(self, model_obj: Any, name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        model_path = self._model_path(name, ts)
        joblib.dump(model_obj, model_path)
        meta = dict(metadata)
        meta.update({"name": name, "timestamp": ts, "path": model_path})
        # write meta index (append to list)
        meta_list = []
        meta_file = self._meta_path(name)
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf8") as fh:
                    meta_list = json.load(fh)
            except Exception:
                meta_list = []
        meta_list.append(meta)
        with open(meta_file, "w", encoding="utf8") as fh:
            json.dump(meta_list, fh, indent=2)
        return meta

    def load_latest(self, name: str):
        meta_file = self._meta_path(name)
        if not os.path.exists(meta_file):
            raise FileNotFoundError(f"No models for {name}")
        with open(meta_file, "r", encoding="utf8") as fh:
            meta_list = json.load(fh)
        if not meta_list:
            raise FileNotFoundError(f"No models for {name}")
        latest = sorted(meta_list, key=lambda m: m["timestamp"])[-1]
        model = joblib.load(latest["path"])
        return model, latest

    def list_models(self, name: str):
        meta_file = self._meta_path(name)
        if not os.path.exists(meta_file):
            return []
        with open(meta_file, "r", encoding="utf8") as fh:
            return json.load(fh)
