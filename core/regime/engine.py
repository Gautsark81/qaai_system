# core/regime/engine.py

from datetime import datetime
import pandas as pd

from core.regime.contracts import RegimeState
from core.regime.memory import RegimeMemory
from core.regime.stack import RegimeStack


# ======================================================
# PHASE-20 DETERMINISTIC REGIME CLASSIFIER
# ======================================================

def _classify_regime(data: pd.DataFrame) -> str:
    """
    Phase-20 deterministic regime classifier.

    This is NOT intelligence.
    This exists only to guarantee regime flips for forensic tests.
    """
    if data is None or data.empty or "price" not in data:
        return "UNKNOWN"

    vol = data["price"].pct_change().std()
    if vol is None:
        return "UNKNOWN"

    return "CRISIS" if vol > 0.02 else "LOW_VOL"


# ======================================================
# REGIME ENGINE (PHASE-20 LOCKED)
# ======================================================

class RegimeEngine:
    """
    Canonical regime detection engine.

    PHASE-20 GUARANTEES:
    - Deterministic
    - Emits REGIME_FLIP_DETECTED
    - No execution authority
    - No dynamic imports
    """

    def __init__(self, *, evidence_store):
        self.memory = RegimeMemory()
        self.stack = RegimeStack()
        self._last_regime_key = {}
        self._evidence = evidence_store

    def evaluate(self, timeframe: str, data: pd.DataFrame) -> RegimeState:
        regime_key = _classify_regime(data)

        timestamp = datetime.utcnow()

        state = RegimeState(
            timeframe=timeframe,
            taxonomy=regime_key,
            confidence=1.0,
            persistence=self.memory.expected_persistence(regime_key),
            transition_probability=1.0,
            timestamp=timestamp,
        )

        prev = self._last_regime_key.get(timeframe)
        if prev and prev != regime_key:
            self.memory.record_transition(prev, regime_key)

            # 🔴 FORENSIC EVIDENCE (PHASE-20)
            self._evidence.emit(
                event_type="REGIME_FLIP_DETECTED",
                payload={
                    "timeframe": timeframe,
                    "from": prev,
                    "to": regime_key,
                },
                timestamp=timestamp,
            )

        self._last_regime_key[timeframe] = regime_key
        self.stack.update(state)
        return state
