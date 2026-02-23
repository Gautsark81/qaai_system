from typing import Optional
from domain.model_ops.model_id import ModelID


class ActiveModelPointer:
    """
    Points to currently active model.
    """

    def __init__(self):
        self._active: Optional[ModelID] = None

    def set(self, model: ModelID) -> None:
        self._active = model

    def get(self) -> Optional[ModelID]:
        return self._active
