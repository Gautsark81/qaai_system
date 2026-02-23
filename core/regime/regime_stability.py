# core/regime/regime_stability.py

from typing import Dict
from statistics import mean

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime


class RegimeStability:
    def __init__(self, memory: RegimeMemory):
        self._memory = memory

    def switch_count(self, symbol: str) -> int:
        events = self._memory.get_history(symbol)
        if len(events) < 2:
            return 0

        switches = 0
        prev_regime = events[0].regime
        for event in events[1:]:
            if event.regime != prev_regime:
                switches += 1
                prev_regime = event.regime
        return switches

    def average_regime_duration(self, symbol: str) -> float:
        durations = self._memory.get_regime_durations(symbol)
        if not durations:
            return 0.0
        return mean(durations.values())

    def stability_score(self, symbol: str) -> float:
        events = self._memory.get_history(symbol)
        if len(events) < 2:
            return 1.0

        switches = self.switch_count(symbol)
        max_possible_switches = len(events) - 1

        if max_possible_switches <= 0:
            return 1.0

        score = 1.0 - (switches / max_possible_switches)
        return max(0.0, min(1.0, score))

    def confidence_trend(self, symbol: str) -> Dict[str, float]:
        events = self._memory.get_history(symbol)
        if not events:
            return {"min": 0.0, "max": 0.0, "mean": 0.0}

        confidences = [e.confidence for e in events]
        return {
            "min": min(confidences),
            "max": max(confidences),
            "mean": mean(confidences),
        }
