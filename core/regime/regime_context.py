# core/regime/regime_context.py

from types import MappingProxyType
from typing import Dict, Any, Optional

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_stability import RegimeStability
from core.regime.regime_transition import RegimeTransition
from core.regime.regime_types import MarketRegime


class RegimeContext:
    def __init__(self, memory: RegimeMemory):
        self._memory = memory
        self._stability = RegimeStability(memory)
        self._transition = RegimeTransition(memory)

    def snapshot(self, symbol: str) -> Dict[str, Any]:
        latest = self._memory.get_latest(symbol)
        current_regime: Optional[MarketRegime] = (
            latest.regime if latest else None
        )

        snapshot = {
            "current_regime": current_regime,
            "stability_score": self._stability.stability_score(symbol),
            "switch_count": self._stability.switch_count(symbol),
            "transition_frequency": self._transition.transition_frequency(symbol),
            "dominant_transition": self._transition.dominant_transition(symbol),
            "confidence_stats": self._stability.confidence_trend(symbol),
        }

        # Return a read-only mapping
        return MappingProxyType(snapshot)
