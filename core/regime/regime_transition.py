# core/regime/regime_transition.py

from collections import Counter
from typing import Dict, Tuple, Optional

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime


class RegimeTransition:
    def __init__(self, memory: RegimeMemory):
        self._memory = memory

    def transition_matrix(self, symbol: str) -> Dict[Tuple[MarketRegime, MarketRegime], int]:
        events = self._memory.get_history(symbol)
        transitions = Counter()

        if len(events) < 2:
            return dict(transitions)

        for prev, curr in zip(events, events[1:]):
            if prev.regime != curr.regime:
                transitions[(prev.regime, curr.regime)] += 1

        return dict(transitions)

    def last_transition(self, symbol: str) -> Optional[Dict[str, object]]:
        events = self._memory.get_history(symbol)
        if len(events) < 2:
            return None

        for prev, curr in zip(reversed(events[:-1]), reversed(events[1:])):
            if prev.regime != curr.regime:
                return {
                    "from": prev.regime,
                    "to": curr.regime,
                    "at": curr.timestamp,
                }

        return None

    def transition_frequency(self, symbol: str) -> float:
        events = self._memory.get_history(symbol)
        if len(events) < 2:
            return 0.0

        transitions = self.transition_matrix(symbol)
        total_transitions = sum(transitions.values())
        total_events = len(events)

        if total_events <= 1:
            return 0.0

        return total_transitions / (total_events - 1)

    def dominant_transition(self, symbol: str) -> Optional[Tuple[MarketRegime, MarketRegime]]:
        transitions = self.transition_matrix(symbol)
        if not transitions:
            return None

        return max(transitions.items(), key=lambda item: item[1])[0]
