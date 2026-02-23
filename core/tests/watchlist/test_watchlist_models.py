from core.watchlist.models import WatchlistEntry


def test_entry_immutable():
    e = WatchlistEntry("A", 0.9, 1, {})
    assert e.symbol == "A"
