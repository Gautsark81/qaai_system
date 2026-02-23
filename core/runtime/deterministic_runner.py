# core/runtime/deterministic_runner.py

import pandas as pd
from collections import defaultdict
from datetime import timedelta

from core.regime.engine import RegimeEngine
from core.runtime.deterministic_context import DeterministicContext


class DeterministicRunner:
    """
    Deterministic execution runner for Phase-20 replay.

    RESPONSIBILITIES:
    - Accept market ticks
    - Build deterministic feature windows
    - Invoke RegimeEngine
    - Allow forensic evidence emission

    GUARANTEES:
    - No randomness
    - No execution authority
    - No strategy mutation
    """

    def __init__(self, *, regime_engine: RegimeEngine):
        self._regime_engine = regime_engine
        self._buffers = defaultdict(list)
        self._tick_count = 0

    # =========================================================
    # 🔴 CANONICAL PHASE-20 ENTRYPOINT
    # =========================================================

    def evaluate_market_tick(self, tick):
        """
        Feed a single market tick into the regime engine.
        """

        timeframe = "TICK"

        self._tick_count += 1

        # 🔒 Deterministic timestamp (NOT utcnow)
        self._buffers[timeframe].append(
            {
                "timestamp": DeterministicContext.now(),
                "price": float(tick.price),
                "volume": float(tick.volume),
            }
        )

        # Require minimal stable window
        if len(self._buffers[timeframe]) < 5:
            return

        df = pd.DataFrame(self._buffers[timeframe])

        # 🔴 REQUIRED — regime detection + evidence emission
        self._regime_engine.evaluate(
            timeframe=timeframe,
            data=df,
        )

    # =========================================================
    # RUNTIME COMPATIBILITY (NO-OP BY DESIGN)
    # =========================================================

    def run_for(self, duration: timedelta):
        """
        Deterministic runner does not advance time autonomously.
        Market ticks drive execution.
        """
        return None

    def run_until_complete(self):
        """
        No background execution loop exists in deterministic replay.
        """
        return None

    def reset(self):
        self._buffers.clear()
        self._tick_count = 0

    def fingerprint(self):
        """
        Stable fingerprint required by runtime.
        """
        return "deterministic-runner-phase20"
