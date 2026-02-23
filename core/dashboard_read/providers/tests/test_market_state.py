from core.dashboard_read.providers.market_state import build_market_state
from core.dashboard_read.snapshot import MarketState


def test_market_state(monkeypatch):
    class DummyRegime:
        volatility = "HIGH"
        liquidity = "LOW"
        stress_level = "SEVERE"

    class DummyExtreme:
        active = True
        classification = "CRASH"

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.market.read_market_regime",
        lambda: DummyRegime(),
    )
    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.market.read_extreme_event_state",
        lambda: DummyExtreme(),
    )
    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.market.read_market_session",
        lambda: "open",
    )

    state = build_market_state()

    assert isinstance(state, MarketState)
    assert state.session == "open"
