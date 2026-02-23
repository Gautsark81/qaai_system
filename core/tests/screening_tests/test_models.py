from core.screening.models import MarketSnapshot


def test_market_snapshot_immutable():
    snap = MarketSnapshot("A", 100, 1e6, 2.0, 0.3, 0.8)
    assert snap.symbol == "A"
