# core/ml/model_registry.py

from typing import Dict


class ModelRegistry:
    """
    Registry of approved ML models.
    Prevents shadow models.
    """

    def __init__(self):
        self._models: Dict[str, object] = {}

    def register(self, name: str, model: object):
        if name in self._models:
            raise RuntimeError("Model already registered")
        self._models[name] = model

    def get(self, name: str):
        if name not in self._models:
            raise RuntimeError("Model not registered")
        return self._models[name]

    def list_models(self):
        return list(self._models.keys())
