from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegimeFlipDetected:
    previous: str
    current: str
    ts: int


class RegimeFlipSentinel:
    """
    TEST-ONLY forensic sentinel.

    Purpose:
    - Observe regime transitions during replay
    - Emit explicit defensive evidence
    - No trading, no capital, no authority
    """

    def __init__(self, evidence_store):
        self._last_regime: Optional[str] = None
        self._evidence = evidence_store

    def observe(self, ts: int, regime: str):
        if self._last_regime is None:
            self._last_regime = regime
            return

        if regime != self._last_regime:
            self._evidence.emit(
                event_type="REGIME_FLIP_DETECTED",
                payload={
                    "previous": self._last_regime,
                    "current": regime,
                    "ts": ts,
                },
            )
            self._last_regime = regime
