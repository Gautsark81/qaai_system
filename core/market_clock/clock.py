from datetime import time

from core.market_clock.config import MarketClockConfig
from core.market_clock.session import MarketSession
from core.market_clock.snapshot import MarketClockSnapshot


class MarketClock:
    """
    Phase 13.2 — Market Clock Authority.

    Single canonical source of market time.
    Deterministic, replayable, and side-effect free.
    """

    # NSE canonical hours
    _MARKET_OPEN = time(9, 15)
    _MARKET_CLOSE = time(15, 30)

    def __init__(self, *, config: MarketClockConfig | None = None):
        self._config = config or MarketClockConfig()

    @property
    def is_enabled(self) -> bool:
        return bool(self._config.enable_market_clock)

    def is_market_open(self, session: MarketSession) -> bool:
        """
        Pure market-hours check.
        """
        if not self.is_enabled:
            return False

        return self._MARKET_OPEN <= session.current_time <= self._MARKET_CLOSE

    def snapshot(self, session: MarketSession) -> MarketClockSnapshot:
        """
        Deterministic, replayable snapshot.

        Produces no side effects and carries no authority.
        """
        return MarketClockSnapshot(
            is_market_open=self.is_market_open(session),
            has_execution_authority=False,
            has_capital_authority=False,
        )
