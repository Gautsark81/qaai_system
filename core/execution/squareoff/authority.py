from __future__ import annotations

from typing import Optional

from core.market_clock.nse_clock import NSEMarketClock
from core.safety.kill_switch import GlobalKillSwitch

from .intent import SquareOffIntent
from .reasons import SquareOffReason


class ForcedSquareOffAuthority:
    """
    Highest-level authority for flattening capital.

    This class:
    - Does NOT place orders
    - Does NOT know brokers
    - Does NOT retry
    - Does NOT allow bypass

    It ONLY decides WHETHER a forced square-off must happen.
    """

    def __init__(
        self,
        *,
        kill_switch: Optional[GlobalKillSwitch] = None,
        market_clock: Optional[NSEMarketClock] = None,
    ):
        self._kill_switch = kill_switch
        self._market_clock = market_clock
        self._latched_intent: Optional[SquareOffIntent] = None

    def evaluate(self) -> Optional[SquareOffIntent]:
        """
        Evaluate whether a forced square-off is required.

        Returns:
            SquareOffIntent if required, else None
        """

        # Idempotency: once triggered, always return the same intent
        if self._latched_intent is not None:
            return self._latched_intent

        # 1️⃣ Global Kill Switch dominates everything
        if self._kill_switch and self._kill_switch.is_active:
            self._latched_intent = SquareOffIntent.create(
                SquareOffReason.KILL_SWITCH
            )
            return self._latched_intent

        # 2️⃣ Market square-off buffer (NSE)
        if self._market_clock:
            state = self._market_clock.session_state
            if state.name == "SQUARE_OFF_BUFFER":
                self._latched_intent = SquareOffIntent.create(
                    SquareOffReason.MARKET_CLOSE
                )
                return self._latched_intent

        # Nothing to do
        return None
