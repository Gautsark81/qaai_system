from core.dashboard_read.builder import SystemSnapshotBuilder
from core.dashboard_read.snapshot import MarketState, MarketRegime


def test_failed_provider_uses_fallback(monkeypatch):
    """
    D-3 GUARANTEE:
    When a provider fails, fallback state is used.
    """

    def explode():
        raise RuntimeError("provider down")

    monkeypatch.setattr(
        "core.dashboard_read.providers.market_state.build_market_state",
        explode,
    )

    builder = SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="test",
    )

    snapshot = builder.build()

    market = snapshot.market_state

    assert isinstance(market, MarketState)
    assert isinstance(market.regime, MarketRegime)
    assert market.regime.volatility == "UNKNOWN"
