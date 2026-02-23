from typing import Dict
from core.regime.contracts import RegimeState


class RegimeStack:
    """
    Holds regime states across timeframes.
    """

    def __init__(self):
        self._states: Dict[str, RegimeState] = {}

    def update(self, state: RegimeState):
        self._states[state.timeframe] = state

    def snapshot(self) -> Dict[str, RegimeState]:
        return dict(self._states)
