from typing import Tuple
from .models import GlobalRegimeState


class RegimeMemoryLedger:
    def __init__(self):
        self._history: Tuple[GlobalRegimeState, ...] = ()

    def append(self, state: GlobalRegimeState) -> None:
        self._history = self._history + (state,)

    def history(self) -> Tuple[GlobalRegimeState, ...]:
        return tuple(self._history)