from dataclasses import dataclass


@dataclass(frozen=True)
class MarketClockSnapshot:
    """
    Read-only snapshot produced by MarketClock.

    Carries NO authority.
    """
    is_market_open: bool

    has_execution_authority: bool = False
    has_capital_authority: bool = False
