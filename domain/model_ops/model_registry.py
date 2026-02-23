from typing import Dict, Optional
from domain.model_ops.model_id import ModelID


class ModelRegistry:
    """
    Authoritative registry of known models.
    """

    def __init__(self):
        self._models: Dict[str, ModelID] = {}

    def register(self, model: ModelID) -> None:
        key = f"{model.name}:{model.version}"
        self._models[key] = model

    def get(self, name: str, version: str) -> Optional[ModelID]:
        return self._models.get(f"{name}:{version}")
