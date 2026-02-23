from datetime import datetime, timezone

from core.live_trading.broker import LiveBrokerStub
from core.watchlist.manager import WatchlistManager
from core.watchlist.models import WatchlistSnapshot


def test_live_broker_stub_accepts_order(monkeypatch):
    snapshot = WatchlistSnapshot(
        entries={
            "NIFTY": {
                "symbol": "NIFTY",
                "rank": 1,
                "score": 1.0,
            }
        },
        created_ts=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        WatchlistManager,
        "get_active_snapshot",
        lambda: snapshot,
    )

    broker = LiveBrokerStub()

    result = broker.place_order(
        symbol="NIFTY",
        qty=1,
        side="BUY",
        price=100.0,
    )

    assert result["status"] == "ACCEPTED"
