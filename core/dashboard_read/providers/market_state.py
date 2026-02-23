from core.dashboard_read.snapshot import (
    MarketState,
    MarketRegime,
    ExtremeEventState,
)

from core.dashboard_read.providers._sources import market as market_source


def build_market_state() -> MarketState:
    """
    Market state provider.

    Rules:
    - Copy-only
    - No logic
    - Schema-accurate
    - Monkeypatch-safe
    """

    regime = market_source.read_market_regime()
    extreme = market_source.read_extreme_event_state()
    session = market_source.read_market_session()

    return MarketState(
        regime=MarketRegime(
            volatility=regime.volatility,
            liquidity=regime.liquidity,
            stress_level=regime.stress_level,
        ),
        extreme_event=ExtremeEventState(
            active=extreme.active,
            classification=extreme.classification,
        ),
        session=session,
    )
