# core/regime/regime_memory.py

from collections import defaultdict
from typing import Dict, List, Optional

from core.regime.regime_event import RegimeEvent
from core.regime.regime_types import MarketRegime


class RegimeMemory:
    def __init__(self):
        super().__setattr__("_events", defaultdict(list))

    def __setattr__(self, key, value):
        if key == "_events":
            raise AttributeError("RegimeMemory is append-only; internal storage is immutable")
        super().__setattr__(key, value)

    def append(
        self,
        symbol: str,
        regime: MarketRegime,
        confidence: float,
        detector_id: str,
        evidence: dict,
    ) -> None:
        if not isinstance(regime, MarketRegime):
            raise ValueError("Invalid regime")

        event = RegimeEvent(
            symbol=symbol,
            regime=regime,
            confidence=confidence,
            detector_id=detector_id,
            evidence=evidence,
        )

        self._events[symbol].append(event)

    def count(self) -> int:
        return sum(len(events) for events in self._events.values())

    def get_latest(self, symbol: str) -> Optional[RegimeEvent]:
        events = self._events.get(symbol, [])
        return events[-1] if events else None

    def get_history(self, symbol: str, window: Optional[int] = None) -> List[RegimeEvent]:
        events = self._events.get(symbol, [])
        if window is None:
            return list(events)
        return list(events[-window:])

    def get_regime_durations(self, symbol: str) -> Dict[MarketRegime, float]:
        events = self._events.get(symbol, [])
        durations: Dict[MarketRegime, float] = defaultdict(float)

        if len(events) < 2:
            return durations

        for prev, curr in zip(events, events[1:]):
            delta = (curr.timestamp - prev.timestamp).total_seconds()
            durations[prev.regime] += max(delta, 0.0)

        return dict(durations)
