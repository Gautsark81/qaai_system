from dataclasses import dataclass


@dataclass(frozen=True)
class MarketClockConfig:
    """
    Explicit enablement contract for Market Clock Authority.
    """
    enable_market_clock: bool = False
